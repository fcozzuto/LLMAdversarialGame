def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # move to increase distance from opponent's corner direction while also approaching opponent
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, ox, oy)
            key = (d, man(nx, ny, w - 1 - ox, h - 1 - oy), abs(nx - ox) + abs(ny - oy))
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # pick resource where we have the largest deterministic advantage over opponent
    best_r = None
    best_adv = -10**9
    best_selfd = 10**9
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer
        if adv > best_adv or (adv == best_adv and sd < best_selfd):
            best_adv = adv
            best_selfd = sd
            best_r = (rx, ry)

    rx, ry = best_r

    # choose move that maximizes advantage on the target resource, with obstacle-safe tiebreakers
    chosen = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = man(nx, ny, rx, ry)
        nod = man(nx, ny, ox, oy)  # mild pressure to not wander too far
        # advantage relative to opponent if we head toward same resource
        # (opponent is assumed to keep moving; we use current opponent distance as proxy)
        score = (best_adv + (man(ox, oy, rx, ry) - nsd), -nsd, -nod, abs(nx - ox) + abs(ny - oy))
        if chosen is None or score > chosen[0]:
            chosen = (score, [dx, dy])

    return chosen[1] if chosen is not None else [0, 0]