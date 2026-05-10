def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for c in (observation.get("obstacles", []) or []):
        if c is not None and len(c) >= 2 and c[0] is not None and c[1] is not None:
            obstacles.add((int(c[0]), int(c[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", None) or []
    best_t = None
    best_d = None
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        if best_d is None or d < best_d:
            best_d = d
            best_t = (rx, ry)
    tx, ty = best_t if best_t is not None else (ox, oy)

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dtx = nx - tx
        dty = ny - ty
        dist_target = dtx * dtx + dty * dty
        dox = nx - ox
        doy = ny - oy
        dist_opp = dox * dox + doy * doy
        score = -dist_target + 0.08 * dist_opp
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]