def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            for kx, ky in (("x", "y"), ("posx", "posy"), ("position", "position")):
                if kx in v and ky in v:
                    return int(v[kx]), int(v[ky])
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
            if isinstance(p, dict) and ("x" in p and "y" in p):
                return int(p["x"]), int(p["y"])
        return None

    s = get_pos(observation.get("self_position", None))
    o = get_pos(observation.get("opponent_position", None))
    if s is None:
        s = (0, 0)
    if o is None:
        o = s
    sx, sy = s
    ox, oy = o

    obstacles = set()
    for it in (observation.get("obstacles", None) or []):
        p = get_pos(it)
        if p is None:
            continue
        x, y = p
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res = []
    for it in (observation.get("resources", None) or []):
        p = get_pos(it)
        if p is None:
            continue
        x, y = p
        if inb(x, y):
            res.append((x, y))

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if not res:
        cx, cy = w // 2, h // 2
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = md((nx, ny), (ox, oy)) * 2 - md((nx, ny), (cx, cy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    my_best = min(md((sx, sy), r) for r in res)
    opp_best = min(md((ox, oy), r) for r in res)
    target = None
    best_t = 10**9
    for r in res:
        am = md((sx, sy), r)
        bm = md((ox, oy), r)
        pr = am - bm  # prefer resources where we're closer than opponent
        if pr < best_t:
            best_t = pr
            target = r

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dres = md((nx, ny), target)
        dop = md((nx, ny), (ox, oy))
        improvement = my_best - dres
        v = improvement * 10 + dop - (opp_best - md((ox, oy), target))
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]] if best else [0, 0]