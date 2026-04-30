def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        # No resources: move toward center to be safe
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestd = 10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
                    if d < bestd:
                        bestd = d
                        best = [dx, dy]
        return best

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    center = ((w - 1) / 2.0, (h - 1) / 2.0)
    # Pick two best resources: nearest to us and nearest to opponent
    nearest_to_us = min(resources, key=lambda r: dist2((sx, sy), r))
    nearest_to_op = min(resources, key=lambda r: dist2((ox, oy), r))

    # Target logic: when opponent is closer to the nearest resource, try to contest it; else go for our nearest.
    us_d = dist2((sx, sy), nearest_to_us)
    op_d = dist2((ox, oy), nearest_to_us)
    target = nearest_to_us if us_d <= op_d else nearest_to_op

    # Evaluate moves: avoid obstacles, go to target, and deny opponent by increasing their distance to target.
    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d_to_target = dist2((nx, ny), target)
            d_to_center = dist2((nx, ny), center)
            d_opp_to_target = dist2((ox, oy), target)
            d_opp_from_n = dist2((ox, oy), (nx, ny))

            # If stepping onto a resource, strongly prefer it.
            on_res = 1 if (nx, ny) in set(tuple(r) for r in resources) else 0

            # Denial term: our move that makes opponent less likely to reach target sooner.
            # (We approximate by pushing the opponent away from our position while they remain on their current tile.)
            # Also add a slight bias to reduce their distance to us (bail out) only if we contest.
            contest = 1 if target == nearest_to_op and op_d < us_d else 0
            denial = (d_opp_from_n - d_opp_to_target) * (3.0 if contest else 1.0)

            score = (-1.2 * d_to_target) + (-0.05 * d_to_center) + (30.0 * on_res) + (0.03 * denial)
            # Small deterministic tie-breaker toward staying/center
            score += (-0.001 * (dx * dx + dy * dy)) + (0.000001 * (nx - sx) * (ny - sy))

            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    # If all moves blocked (rare), stay.
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]