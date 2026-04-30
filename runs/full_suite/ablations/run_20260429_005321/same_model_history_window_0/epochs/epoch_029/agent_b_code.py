def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((o[0], o[1]) for o in obstacles_list)

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    best_r = None
    best_score = None
    for r in resources:
        rx, ry = r[0], r[1]
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            d_self = dist2(sx, sy, rx, ry)
            d_opp = dist2(ox, oy, rx, ry)
            score = d_self - 0.8 * d_opp
            if best_score is None or score < best_score:
                best_score = score
                best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        val = dist2(nx, ny, tx, ty) - 0.05 * dist2(nx, ny, ox, oy)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]