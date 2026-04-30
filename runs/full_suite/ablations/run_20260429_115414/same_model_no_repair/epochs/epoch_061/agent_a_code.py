def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        return [0, 0]

    best_res = None
    best_val = None
    best_self_d = None
    for r in resources:
        rx, ry = r
        d_s = dist((sx, sy), (rx, ry))
        d_o = dist((ox, oy), (rx, ry))
        val = d_o - d_s
        if best_val is None or val > best_val or (val == best_val and d_s < best_self_d):
            best_val, best_self_d, best_res = val, d_s, (rx, ry)

    tx, ty = best_res
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_prev_to_target = dist((sx, sy), (tx, ty))

    best_move = [0, 0]
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        self_d = dist((nx, ny), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))
        self_to_opp = dist((nx, ny), (ox, oy))

        advance = self_prev_to_target - self_d
        score = (opp_d - self_d) + 0.05 * advance + 0.01 * self_to_opp
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move