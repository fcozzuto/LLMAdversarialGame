def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res_list.append((x, y))
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
            if 0 <= x < w and 0 <= y < h:
                res_list.append((x, y))

    deltas = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    tx, ty = ox, oy
    if res_list:
        best = None
        bd = None
        for x, y in res_list:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if bd is None or d < bd:
                bd = d
                best = (x, y)
        tx, ty = best

    best_move = (0, 0)
    best_d = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if best_d is None or d < best_d:
            best_d = d
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]