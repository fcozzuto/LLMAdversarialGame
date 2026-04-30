def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best = (0, 0)
    bestv = -10**18
    toward_opponent = man(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = 0
        if res:
            dcur = 10**9
            dnew = 10**9
            for rx, ry in res:
                dc = man(sx, sy, rx, ry)
                if dc < dcur: dcur = dc
                dn = man(nx, ny, rx, ry)
                if dn < dnew: dnew = dn
            val += 1000 * (dcur - dnew)
            val -= 5 * man(nx, ny, ox, oy)
        else:
            val += 20 * (man(nx, ny, ox, oy) - toward_opponent)
        if val > bestv or (val == bestv and (dx, dy) < best):
            bestv = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]