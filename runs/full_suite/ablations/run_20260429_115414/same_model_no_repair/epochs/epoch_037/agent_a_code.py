def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Select target: best advantage for us (arrive earlier / more strongly).
    best_t = None
    best_adv = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in blocked:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if best_t is None or adv > best_adv or (adv == best_adv and ds < cheb(sx, sy, best_t[0], best_t[1])):
            best_adv = adv
            best_t = (rx, ry)

    if best_t is None:
        # No reachable resource; move toward any non-blocked resource direction deterministically.
        for rx, ry in resources:
            if inb(rx, ry) and (rx, ry) not in blocked:
                tx, ty = rx, ry
                dx = 0 if tx == sx else (1 if tx > sx else -1)
                dy = 0 if ty == sy else (1 if ty > sy else -1)
                return [dx, dy]
        return [0, 0]

    tx, ty = best_t

    # Evaluate our next move with an "opponent likely to chase target" approximation.
    best_m = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        our_next = cheb(nx, ny, tx, ty)
        opp_best = 10**9
        for odx, ody in moves:
            nxx, nyy = ox + odx, oy + ody
            if not inb(nxx, nyy) or (nxx, nyy) in blocked:
                continue
            d = cheb(nxx, nyy, tx, ty)
            if d < opp_best:
                opp_best = d
        score = (opp_best - our_next) - 0.01 * our_next  # maximize relative advantage, slight push to quicker capture
        if best_score is None or score > best_score:
            best_score = score
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]