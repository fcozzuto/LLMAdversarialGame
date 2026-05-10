def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resset.add((int(p[0]), int(p[1])))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da + db

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = -10**18

    if resset:
        reslist = list(resset)
        for dx0, dy0 in deltas:
            nx, ny = x + dx0, y + dy0
            if not inb(nx, ny):
                continue
            score = 0
            if (nx, ny) in resset:
                score += 1000000
            # Choose the resource where (my advantage) is greatest.
            best_adv = -10**18
            for rx, ry in reslist:
                myd = man(nx, ny, rx, ry)
                oppd = man(ox, oy, rx, ry)
                adv = (-myd) + 0.9 * oppd
                if (rx, ry) in resset and myd == 0:
                    adv += 1000
                if adv > best_adv:
                    best_adv = adv
            score += best_adv
            # Mild tie-break: stay closer to opponent late game to reduce their access.
            tr = int(observation.get("turns_remaining", 0) or 0)
            score += 0.001 * man(nx, ny, ox, oy) - 0.0001 * tr
            if score > best_score:
                best_score = score
                best = [dx0, dy0]
        return best

    # No visible resources: move toward the center-corner away from opponent to contest later.
    cx, cy = w // 2, h // 2
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
    if man(x, y, cx, cy) < 6:
        tx, ty = cx, cy

    best = [0, 0]
    best_score = -10**18
    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            continue
        score = -man(nx, ny, tx, ty) + 0.05 * man(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best = [dx0, dy0]
    return best