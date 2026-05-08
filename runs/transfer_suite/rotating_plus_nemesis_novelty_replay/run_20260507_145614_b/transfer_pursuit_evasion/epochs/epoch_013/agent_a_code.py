def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    resources = observation.get("resources", []) or []
    best_t = None
    best_td = None
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
        except Exception:
            continue
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obst:
            continue
        d = dist2(sx, sy, rx, ry)
        if best_td is None or d < best_td:
            best_td, best_t = d, (rx, ry)

    if best_t is not None:
        tx, ty = best_t
    else:
        tx, ty = (ox, oy) if (0 <= ox < w and 0 <= oy < h) else (w // 2, h // 2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_t = dist2(nx, ny, tx, ty)
        d_o = dist2(nx, ny, ox, oy)
        score = d_t * 1000 - d_o  # prioritize reaching target; also slightly press opponent
        if best_score is None or score < best_score:
            best_score, best_move = score, [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move