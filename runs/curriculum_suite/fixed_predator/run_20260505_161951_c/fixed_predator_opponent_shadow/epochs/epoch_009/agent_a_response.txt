def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        best = None
        best_adv = -10**18
        best_sd = 10**18
        best_rx, best_ry = None, None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            if adv > 0:
                if adv > best_adv or (adv == best_adv and sd < best_sd) or (adv == best_adv and sd == best_sd and (rx, ry) < (best_rx, best_ry)):
                    best_adv = adv
                    best_sd = sd
                    best = (rx, ry)
                    best_rx, best_ry = rx, ry
        if best is None:
            # No resource where we're closer; take the closest while also breaking ties deterministically.
            best_sd = 10**18
            for rx, ry in resources:
                sd = man(sx, sy, rx, ry)
                if sd < best_sd or (sd == best_sd and (rx, ry) < (best_rx, best_ry)):
                    best_sd = sd
                    best = (rx, ry)
                    best_rx, best_ry = rx, ry
        tx, ty = best
    else:
        # No resources: move to maximize distance from opponent.
        best = None
        best_score = -10**18
        for dx, dy, nx, ny in moves:
            sdist = man(nx, ny, ox, oy)
            if sdist > best_score or (sdist == best_score and (nx, ny) < best):
                best_score = sdist
                best = (nx, ny)
        nx, ny = best
        return [max(-1, min(1, nx - sx)), max(-1, min(1, ny - sy))]

    # Choose move minimizing distance to target; tie-break by improving relative contest vs opponent.
    best_move = None
    best_ms = 10**18
    best_tiebreak = -10**18
    best_nxy = None
    for dx, dy, nx, ny in moves:
        d_to_t = man(nx, ny, tx, ty)
        self_dist_after = man(nx, ny, ox, oy)
        opp_dist = man(ox, oy, tx, ty)
        self_dist = man(nx, ny, tx, ty)
        contest_after = opp_dist - self_dist  # higher means we are closer than opponent to target
        ms = d_to_t
        tb = contest_after
        if ms < best_ms or (ms == best_ms and tb > best_tiebreak) or (ms == best_ms and tb == best_tiebreak and (nx, ny) < best_nxy):
            best_ms = ms
            best_tiebreak = tb
            best_move = (dx, dy)
            best_nxy = (nx, ny)

    return [best_move[0], best_move[1]]