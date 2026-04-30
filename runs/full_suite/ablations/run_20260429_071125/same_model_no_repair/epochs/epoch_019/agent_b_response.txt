def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def risk(x, y):
        if (x, y) in occ:
            return 10**9
        r = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (x + dx, y + dy) in occ:
                r += 7
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in occ:
                r += 3
        return r

    if not resources:
        return [0, 0]

    # Choose a target resource we can likely reach earlier than opponent (with safety bias).
    best_t = None
    best_sc = -10**18
    for rx, ry in resources:
        if (rx, ry) in occ:
            continue
        dm = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        if do == 0 and dm > 0:
            continue
        opp_adv = do - dm  # positive => we are closer
        sc = opp_adv * 55 - dm * 2
        # penalize targets adjacent to obstacles to avoid funneling into dead zones
        sc -= risk(rx, ry) * 0.8
        # extra preference for closer resources when advantage is similar
        sc -= 2 * min(abs(rx - sx), abs(ry - sy))
        if sc > best_sc:
            best_sc = sc
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    rx, ry = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cur_dm = manh(sx, sy, rx, ry)
    best = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        dm = manh(nx, ny, rx, ry)
        do = manh(ox, oy, rx, ry)
        adv = do - dm
        # Encourage reducing distance; discourage giving opponent advantage.
        v = adv * 45 - dm * 2 - risk(nx, ny) * 1.6
        # If we are not improving distance, heavily discount unless safe and already close.
        if dm >= cur_dm and dm > 1:
            v -= 60
        # If we get too close to obstacles, discourage diagonals around them
        if dx != 0 and dy != 0 and risk(nx, ny) > 10:
            v -= 10
        if v > best_v:
            best_v = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]