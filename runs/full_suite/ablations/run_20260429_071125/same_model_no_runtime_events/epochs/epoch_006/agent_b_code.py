def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    def valid_moves():
        ms = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    ms.append((dx, dy))
        return ms

    moves = valid_moves()
    if not moves:
        return [0, 0]

    # If no resources, drift to increase distance from opponent while moving toward nearest corner.
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda c: cheb(sx, sy, c[0], c[1]))
        best = None; bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy) * 2 - cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    # Pick a target where we are relatively closer, with a small preference for nearer resources.
    best_target = None; best_tkey = (-10**18, 10**18)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # advantage for us; tie-break by absolute closeness
        adv = do - ds
        tkey = (adv, ds)
        if tkey > best_tkey:
            best_tkey = tkey
            best_target = (rx, ry)

    rx, ry = best_target
    # Evaluate each possible move with a robust 1-step lookahead:
    # - maximize our progress toward target
    # - if tied, deny opponent by increasing opponent distance to target
    # - also avoid getting too close to opponent.
    best = None; bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        progress = cheb(sx, sy, rx, ry) - ds2
        opp_away = cheb(nx, ny, ox, oy)
        v = progress * 100 + (do2 - ds2) * 10 + opp_away
        if v > bestv:
            bestv = v; best = (dx, dy)

    return [best[0], best[1]] if best else [0, 0]