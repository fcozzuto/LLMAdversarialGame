def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))

    obs = set((int(x), int(y)) for x, y in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    val = []
    for x, y in resources:
        x, y = int(x), int(y)
        if not inb(x, y) or (x, y) in obs:
            continue
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # primary: reach first (positive advantage). secondary: earlier arrival. tertiary: larger margin.
        adv = do - ds
        time_pref = 0
        if tr > 0:
            # prefer targets we can likely get (helps determinism near end)
            if ds <= tr: time_pref = 1
            if ds == 0: time_pref = 2
        val.append((adv, time_pref, -ds, -do, x, y))

    if not val:
        return [0, 0]

    val.sort(reverse=True)
    _, _, _, _, tx, ty = val[0]

    def step_towards():
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = []
        candidates.append((dx, dy))
        if dx != 0 and dy != 0:
            candidates.append((dx, 0))
            candidates.append((0, dy))
        # If diagonal is best but blocked, try remaining axis orders that reduce distance
        candidates.append((0, 0))
        best = (0, 0, 10**9, -10**9)  # dx,dy,dist,oppdist (for tie)
        for mdx, mdy in candidates:
            nx, ny = sx + mdx, sy + mdy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            dist = cheb(nx, ny, tx, ty)
            oppdist = cheb(nx, ny, ox, oy)
            # prioritize reducing our distance; then prefer being farther from opponent
            key = (dist, -oppdist)
            if key < (best[2], best[3]):
                best = (mdx, mdy, dist, -oppdist)
        return [best[0], best[1]]

    return step_towards()