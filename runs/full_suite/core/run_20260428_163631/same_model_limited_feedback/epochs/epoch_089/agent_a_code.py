def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    self_pos = observation["self_position"]; opp_pos = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    sx, sy = self_pos; ox, oy = opp_pos

    def in_bounds(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx + dy  # deterministic, simple

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            key = (-(od - sd), sd, abs(rx - ox) + abs(ry - oy))
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t

        best_move = None
        best_score = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            s_to = dist((nx, ny), (tx, ty))
            o_to = dist((ox, oy), (tx, ty))
            s_opp = dist((nx, ny), (ox, oy))
            score = (s_to, -s_opp, -((o_to - s_to)))
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: drift toward center while keeping distance from opponent
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    best_move = None
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        center_d = abs(nx - cx) + abs(ny - cy)
        opp_d = dist((nx, ny), (ox, oy))
        score = (center_d, -opp_d)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]