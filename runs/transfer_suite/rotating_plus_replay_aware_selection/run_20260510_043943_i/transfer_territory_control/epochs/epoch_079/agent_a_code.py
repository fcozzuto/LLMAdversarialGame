def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = observation.get("resources") or []
    res_cells = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h:
            res_cells.append((x, y))
    if not res_cells:
        res_cells = [(sx, sy)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_dist2(x, y):
        dmin = None
        for rx, ry in res_cells:
            dx, dy = rx - x, ry - y
            d = dx * dx + dy * dy
            if dmin is None or d < dmin:
                dmin = d
        return dmin if dmin is not None else 0

    best = dirs[0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_res = best_dist2(nx, ny)
        dxo, dyo = ox - nx, oy - ny
        d_opp = dxo * dxo + dyo * dyo
        score = -d_res + 0.2 * d_opp
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]