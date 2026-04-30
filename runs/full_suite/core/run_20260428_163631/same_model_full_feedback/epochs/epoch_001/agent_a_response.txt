def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def safe(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    # Select target resource that we are relatively closest to compared to opponent
    if resources:
        best_res = resources[0]
        best_adv = None
        for r in resources:
            self_d = dist2((sx, sy), r)
            opp_d = dist2((ox, oy), r)
            adv = opp_d - self_d  # higher means we're closer
            if best_adv is None or adv > best_adv:
                best_adv = adv
                best_res = r
            elif adv == best_adv:
                # deterministic tie-break: smaller self distance, then lexicographic
                if self_d < dist2((sx, sy), best_res) or (self_d == dist2((sx, sy), best_res) and r < best_res):
                    best_res = r
        tx, ty = best_res
    else:
        # No resources: head to farthest corner from opponent (deterministic)
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        target = max(corners, key=lambda c: (dist2((ox, oy), c), -c[0], -c[1]))
        tx, ty = target

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            # invalid/blocked: treat as staying but heavily penalize
            nx, ny = sx, sy
            blocked_pen = 1
        else:
            blocked_pen = 0

        d_to_target = dist2((nx, ny), (tx, ty))
        d_to_opp = dist2((nx, ny), (ox, oy))

        # Move evaluation: primarily closer to target, secondarily farther from opponent
        val = (-d_to_target, d_to_opp)
        # Add slight penalty for blocked moves
        if blocked_pen:
            val = (val[0] - 1000000, val[1])

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]