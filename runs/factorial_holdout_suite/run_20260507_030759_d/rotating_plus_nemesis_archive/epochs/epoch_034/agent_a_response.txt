def choose_move(observation):
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    res = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if res:
        best_t = None
        best_k = None
        for rx, ry in res:
            md = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            k = md - 0.9 * od  # prefer resources we can reach sooner than opponent
            if best_k is None or k < best_k or (k == best_k and (md, rx, ry) < (best_k_m, best_tx, best_ty)):
                best_k = k
                best_t = (rx, ry)
                best_k_m = md
                best_tx, best_ty = rx, ry
        tx, ty = best_t

        best_move = (0, 0)
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obst:
                continue
            if (nx, ny) == (sx, sy) and (tx, ty) != (sx, sy):
                step = 1
            else:
                step = 0
            nmd = man(nx, ny, tx, ty)
            nod = man(ox + dx if inside(ox + dx, oy) else ox, oy + dy if inside(ox, oy + dy) else oy, tx, ty)
            val = nmd + 0.2 * nod + 0.01 * step
            if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: drift toward center while avoiding obstacles
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        val = man(nx, ny, cx, cy)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]