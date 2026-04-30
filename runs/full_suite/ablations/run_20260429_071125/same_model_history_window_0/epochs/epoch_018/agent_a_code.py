def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    center = (w // 2, h // 2)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # If we can reach a resource sooner than opponent, prioritize it; otherwise reposition.
        if resources:
            local_best = -10**9
            for rx, ry in resources:
                s_d = dist((nx, ny), (rx, ry))
                o_d = dist((ox, oy), (rx, ry))
                # positive means we are advantaged toward that resource
                takeover = o_d - s_d
                # slightly prefer being closer to the target and farther from being boxed near obstacles is implicit
                val = takeover * 100 - s_d * 5
                if (rx, ry) == (nx, ny):
                    val += 1000  # prioritize picking up
                if val > local_best:
                    local_best = val
            # also discourage moving to squares that worsen our relative ability
            cur_adv = -min(dist((sx, sy), r) - dist((ox, oy), r) for r in resources)
            rel_penalty = (local_best - cur_adv * 100) * 0  # keep deterministic but neutral
            candidate_val = local_best + rel_penalty
        else:
            candidate_val = -dist((nx, ny), center) - dist((nx, ny), (ox, oy)) * 0.5

        # Tactical response: if opponent is adjacent, prefer moves that increase their distance
        if dist((ox, oy), (nx, ny)) <= 1:
            candidate_val += 30

        if candidate_val > best_val:
            best_val = candidate_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]