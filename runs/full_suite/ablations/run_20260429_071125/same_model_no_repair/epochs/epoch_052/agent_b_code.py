def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Choose target resources that are likely contested: prioritize those where we can be competitive.
    cont = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Score seed: how much closer we are than opponent, then closeness, then position.
        cont.append((opd - myd, myd, -opd, rx, ry))
    cont.sort(reverse=True)
    top = [(c[3], c[4]) for c in cont[:6]] if cont else []

    if not top:
        # fallback to any reachable resource
        top = [(r[0], r[1]) for r in resources[:1]]

    best = (None, -10**18, None, None, None)
    for dx, dy, nx, ny in legal:
        # Avoid dead zones: keep some distance from opponent unless we are clearly winning a target.
        mindiff = -10**18
        mind = 10**18
        for rx, ry in top:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            diff = opd - myd  # positive means we're closer than opponent for this resource
            # Prefer moves that create a strong advantage on at least one resource.
            if diff > mindiff:
                mindiff = diff
            if myd < mind:
                mind = myd
        oppd_now = cheb(nx, ny, ox, oy)
        # Composite: primary advantage; secondary: reach time; tertiary: separation.
        val = mindiff * 1000 - mind + oppd_now * 0.5
        # Deterministic tie-break: smaller dx,dy ordering then position.
        if val > best[1] or (val == best[1] and (dx, dy, nx, ny) < best[2:]):
            best = (dx, dy, dx, dy, nx, ny)
    return [best[0], best[1]]