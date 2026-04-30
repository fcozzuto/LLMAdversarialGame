def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obs

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def min_cheb(x, y, pts):
        if not pts:
            return 999
        md = 999
        for px, py in pts:
            dx = x - px
            if dx < 0: dx = -dx
            dy = y - py
            if dy < 0: dy = -dy
            d = dx if dx > dy else dy
            if d < md: md = d
            if md <= 0: return 0
        return md

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_ob = min_cheb(nx, ny, obs)
        d_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        if res:
            best_r = 999999
            for rx, ry in res:
                d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if d < best_r: best_r = d
        else:
            best_r = 0

        if d_ob <= 0:
            continue
        # Higher is better
        score = (d_op * 0.02) + (2000.0 / (best_r + 1.0)) + (6.0 / (d_ob + 0.5))
        # Slightly prefer forward direction toward our corner away from opponent
        away_dx = 1 if sx < (w - 1) // 2 else -1
        away_dy = 1 if sy < (h - 1) // 2 else -1
        score += 0.05 * ((nx - sx) * away_dx + (ny - sy) * away_dy)

        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]