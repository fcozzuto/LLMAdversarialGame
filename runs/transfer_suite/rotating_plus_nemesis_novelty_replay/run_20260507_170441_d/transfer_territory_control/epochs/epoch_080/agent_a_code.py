def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p is None:
            continue
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    res = observation.get("resources") or []
    res_pos = []
    for p in res:
        if p is None:
            continue
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            res_pos.append((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    un_pos = set()
    for p in unclaimed:
        if p is None:
            continue
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            un_pos.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    bestv = -10**18
    bestdxdy = [0, 0]
    pref = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    prefset = set(pref)

    for dx, dy in pref + [m for m in moves if m not in prefset]:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        v = 0
        if (nx, ny) in un_pos:
            v += 80
        if res_pos:
            d = min(manh(nx, ny, rx, ry) for rx, ry in res_pos)
            v += 30 - 2 * d
        v += 3 * (manh(nx, ny, nx, ny) == 0)
        do = manh(nx, ny, ox, oy)
        v += 10 * do - 2 * do * do // max(1, w + h)
        if best is None or v > bestv:
            best = (nx, ny)
            bestv = v
            bestdxdy = [dx, dy]

    return bestdxdy