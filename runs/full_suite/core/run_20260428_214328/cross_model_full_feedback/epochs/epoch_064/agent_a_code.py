def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 if d1 > d2 else d2

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            x, y = sx + dx, sy + dy
            if inside(x, y) and (x, y) not in obst:
                cand.append((dx, dy))

    if not cand:
        return [0, 0]

    center = (w // 2, h // 2)
    best_move = cand[0]
    best_val = None
    res_list = resources if resources else [center]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        my_pos = (nx, ny)
        if resources:
            my_need = min(cheb(my_pos, r) for r in res_list) if res_list else 999
            opp_need = min(cheb((ox, oy), r) for r in res_list) if res_list else 999
            val = (opp_need - my_need) * 1000 - cheb(my_pos, (ox, oy))
        else:
            val = cheb(my_pos, (ox, oy))
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]