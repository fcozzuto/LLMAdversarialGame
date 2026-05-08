def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = observation.get("resources", None)
    res_list = []
    if isinstance(resources, list) and resources:
        for r in resources:
            if r is None:
                continue
            x, y = r
            res_list.append((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    cur_opp = manh(sx, sy, ox, oy)
    best = (cur_opp, -10**9, 0, 0)

    if not inb(sx, sy):
        sx, sy = ox, oy
        sx, sy = int(sx), int(sy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        oppd = manh(nx, ny, ox, oy)
        if res_list:
            rd = 10**9
            for rx, ry in res_list:
                d = manh(nx, ny, rx, ry)
                if d < rd:
                    rd = d
            # primary: reduce opp distance; tie-break: move toward resources (smaller rd)
            key = (oppd, rd, dx, dy)
            if key < best[:2] + (best[2], best[3]):
                best = (oppd, -rd, dx, dy)
        else:
            key = (oppd, dx, dy)
            if key < (best[0], best[2], best[3]):
                best = (oppd, -10**9, dx, dy)

    return [int(best[2]), int(best[3])]