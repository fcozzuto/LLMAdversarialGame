def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_sc = -10**18
    has_res = bool(resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = 0
        if nx == sx and ny == sy:
            sc -= 1
        if (nx, ny) == (ox, oy):
            sc -= 1000

        if has_res:
            mcur = 10**9
            mnew = 10**9
            for rx, ry in resources:
                if rx == nx and ry == ny:
                    mnew = 0
                    break
                dc = d(sx, sy, rx, ry)
                if dc < mcur:
                    mcur = dc
                dn = d(nx, ny, rx, ry)
                if dn < mnew:
                    mnew = dn
            sc += (mcur - mnew) * 10
            if mnew == 0:
                sc += 5000
            sc -= d(nx, ny, ox, oy)  # keep some distance
        else:
            sc += -d(nx, ny, ox, oy) * 2  # chase score potential

        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best