def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # No resources: drift toward opponent's side to reduce their options.
    if not resources:
        tx = w - 1 if sx < w // 2 else 0
        ty = h - 1 if sy < h // 2 else 0
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): nx, ny = sx, sy
            v = cheb(nx, ny, tx, ty) * -1
            if v > bestv:
                bestv = v
                best = (nx - sx, ny - sy)
        return [best[0], best[1]]

    # Consider a few most relevant resources (closest by current self distance).
    tmp = []
    for rx, ry in resources:
        ds0 = cheb(sx, sy, rx, ry)
        tmp.append((ds0, rx, ry))
    tmp.sort(key=lambda t: (t[0], t[1], t[2]))
    chosen = tmp[:6]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): nx, ny = sx, sy

        v = 0
        # Positive v => we are closer than opponent for that resource; weight by urgency.
        for ds0, rx, ry in chosen:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Margin encourages grabbing/denying; urgency favors nearby resources.
            margin = do - ds
            urgency = 1.0 / (1 + ds0)
            v += margin * (2.0 * urgency) - 0.15 * ds
        # Small tie-break: prefer moving closer to the currently best-looking resource.
        if v == bestv:
            target = chosen[0]
            v2 = -cheb(nx, ny, target[1], target[2])
            if v2 > -cheb(sx + best[0], sy + best[1], target[1], target[2]):
                best = (nx - sx, ny - sy)
                bestv = v

        if v > bestv:
            bestv = v
            best = (nx - sx, ny - sy)

    return [best[0], best[1]]