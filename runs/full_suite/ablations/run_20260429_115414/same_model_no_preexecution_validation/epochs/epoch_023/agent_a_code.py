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
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    res_list = [(int(r[0]), int(r[1])) for r in resources if r is not None and len(r) >= 2]
    if not res_list:
        # New fallback: move to safer corner/center while increasing distance from opponent
        tx, ty = ((w - 1) if sx <= (w - 1) // 2 else 0), ((h - 1) if sy <= (h - 1) // 2 else 0)
        best = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            dv = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            cv = -(nx - tx) * (nx - tx) - (ny - ty) * (ny - ty)
            v = dv + 0.7 * cv
            if v > bestv: bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def eval_state(x, y):
        # Prefer being on resources, then close to nearest resource; avoid opponent closeness
        md = 10**18
        for rx, ry in res_list:
            d = dist2(x, y, rx, ry)
            if d < md: md = d
        on_res = 1 if (x, y) in set(res_list) else 0
        oppd = dist2(x, y, ox, oy)
        # Strong bias to secure a resource while keeping distance from opponent
        return (on_res * 10**6) - 0.8 * md - 2.2 * (1.0 / (1 + oppd))

    def next_pos(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        return (x, y) if not legal(nx, ny) else (nx, ny)

    # Small deterministic lookahead: depth 3, but evaluation uses opponent's current position only
    best_move = (0, 0)
    best_val = -10**18
    for mdx, mdy in dirs:
        x1, y1 = next_pos(sx, sy, mdx, mdy)
        v = eval_state(x1, y1)
        # depth-2 and depth-3 rollouts for us (opponent not simulated; our change is lookahead)
        b2 = -10**18
        for ddx, ddy in dirs:
            x2, y2 = next_pos(x1, y1, ddx, ddy)
            v2 = eval_state(x2, y2)
            b3 = -10**18
            for edx, edy in dirs:
                x3, y3 = next_pos(x2, y2, edx, edy)
                v