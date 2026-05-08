def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells") | to_set("unclaimed")
    opp_terr = to_set("opponent_territory")

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if unclaimed:
        target = min(unclaimed, key=lambda p: md(p, (sx, sy)))
    elif opp_terr:
        target = min(opp_terr, key=lambda p: md(p, (sx, sy)))
    else:
        target = (w // 2, h // 2)

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = -md((nx, ny), target)
        if (nx, ny) in unclaimed:
            v += 10
        if (nx, ny) in opp_terr:
            v += 3
        v += -0.3 * md((nx, ny), (ox, oy))
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best