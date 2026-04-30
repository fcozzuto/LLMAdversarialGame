def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not inside(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d1 = dist(nx, ny, ox, oy)
            val = d1
            if best is None or val > best[0] or (val == best[0] and (nx, ny) < best[1]):
                best = (val, (nx, ny), dx, dy)
        return [best[2], best[3]] if best is not None else [0, 0]

    best_target = None
    best_val = None
    for (rx, ry) in resources[:50]:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        val = (do - ds, -ds, -rx, -ry)
        if best_val is None or val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ds2 = dist(nx, ny, tx, ty)
        dprev = dist(sx, sy, tx, ty)
        opp2 = dist(nx, ny, ox, oy)
        opp1 = dist(sx, sy, ox, oy)
        closer_opp_penalty = 0 if opp2 >= opp1 else (opp1 - opp2)
        val = (-ds2, -closer_opp_penalty, nx, ny)
        if best is None or val > best[0]:
            best = (val, dx, dy)
    return [best[1], best[2]] if best is not None else [0, 0]