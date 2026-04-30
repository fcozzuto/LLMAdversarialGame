def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    def safety(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny): cnt += 1
        return cnt

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            v = -cheb((nx, ny), (cx, cy)) + 0.01 * safety(nx, ny)
            if v > bestv: bestv = v; best = (dx, dy)
        return [int(best[0]), int(best[1])]

    res = []
    for p in resources:
        x, y = int(p[0]), int(p[1])
        if valid(x, y): res.append((x, y))
    if not res:
        return [0, 0]

    best_t = res[0]
    best_key = None
    for t in res:
        ds = cheb((sx, sy), t)
        do = cheb((ox, oy), t)
        # Prefer resources we can reach relatively sooner; break ties by preferring farther from opponent.
        key = (ds - 0.85 * do, ds, -do, t[0], t[1])
        if best_key is None or key < best_key:
            best_key = key
            best_t = t

    tx, ty = best_t
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        # Encourage progress toward target while keeping away from being "cut off" by opponent.
        progress = cheb((nx, ny), (tx, ty))
        opp = cheb((ox, oy), (tx, ty))
        s = safety(nx, ny)
        stay_pen = 0.15 if (dx, dy) == (0, 0) else 0.0
        val = (-progress) + 0.06 * (opp) + 0.01 * s - stay_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]