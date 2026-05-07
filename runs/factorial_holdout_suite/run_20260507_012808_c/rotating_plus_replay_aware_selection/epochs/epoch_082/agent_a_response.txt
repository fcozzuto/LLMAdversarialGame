def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        best_key = (-10**9, 10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (-(cheb(nx, ny, tx, ty)), cheb(nx, ny, tx, ty))
            if key > best_key:
                best_key = key
                best = [dx, dy]
        return best

    res = [tuple(r) for r in resources]
    best_move = [0, 0]
    best_key = (-10**18, -10**18, 10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate the best resource we can realistically contest from this next cell.
        best_adv = -10**18
        best_self_d = 10**18
        best_opp_d = 10**18
        for rx, ry in res:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - self_d  # positive means we are closer
            if adv > best_adv or (adv == best_adv and self_d < best_self_d):
                best_adv = adv
                best_self_d = self_d
                best_opp_d = opp_d

        # Tie-break: take immediate capture if possible; otherwise maximize advantage and closeness.
        immediate = 1 if best_self_d == 0 else 0
        far_pen = best_self_d
        # Additional pressure: prefer moves that also reduce opponent's best reachable cell (coarse).
        opp_current_best = 10**18
        for rx, ry in res:
            opp_current_best = min(opp_current_best, cheb(ox, oy, rx, ry))

        key = (immediate, best_adv, -far_pen, -opp_current_best)
        # Convert to comparable tuple ordering with fixed length
        # (Python compares tuples lexicographically; we just keep consistent dimensions)
        cmp_key = (key[0], key[1], key[2], key[3])
        if cmp_key > best_key:
            best_key = cmp_key
            best_move = [dx, dy]

    return best_move