def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not inside(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    tx, ty = ox, oy
    if resources:
        best = None
        for x, y in resources:
            d = abs(x - sx)
            dd = abs(y - sy)
            cd = d if d > dd else dd
            if best is None or cd < best[0] or (cd == best[0] and (x, y) < (best[1], best[2])):
                best = (cd, x, y)
        tx, ty = best[1], best[2]

    cur_best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = abs(tx - nx)
        dd = abs(ty - ny)
        cd = d if d > dd else dd
        if cur_best is None or cd < cur_best[0] or (cd == cur_best[0] and (dx, dy) < (cur_best[1], cur_best[2])):
            cur_best = (cd, dx, dy)

    if cur_best is None:
        return [0, 0]
    return [cur_best[1], cur_best[2]]