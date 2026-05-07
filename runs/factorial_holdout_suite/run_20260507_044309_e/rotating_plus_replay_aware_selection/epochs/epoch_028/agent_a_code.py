def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = cheb(nx, ny, tx, ty)
                if d < best[0]:
                    best = (d, dx, dy)
        return [best[1], best[2]]

    bestv = -10**18
    target = resources[0]
    best_selfd = 10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; small bias to closer and central.
        center = cheb(rx, ry, w // 2, h // 2)
        v = (do - ds) * 1000 - ds * 2 - center * 0.5
        if v > bestv or (v == bestv and (ds < best_selfd or (ds == best_selfd and (rx, ry) < target))):
            bestv = v
            best_selfd = ds
            target = (rx, ry)

    rx, ry = target
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            ds2 = cheb(nx, ny, rx, ry)
            # Strongly avoid moves that let opponent steal: compare next step lead.
            do = cheb(ox, oy, rx, ry)
            lead_next = do - ds2
            # Tie-break deterministically by smaller ds2, then smaller dx,dy.
            score = (-lead_next) * 1000 + ds2
            cand.append((score, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]