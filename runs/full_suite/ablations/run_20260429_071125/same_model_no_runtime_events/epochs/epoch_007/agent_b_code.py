def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far_corner = min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
        best = None; bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy) - cheb(nx, ny, far_corner[0], far_corner[1])
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Pick move maximizing "resource swing" from the next position:
    # swing = (opponent_distance - self_distance) for the best resource we can potentially contest,
    # plus a small tie-break toward bringing distance down.
    best = None; bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_res = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer grabbing/contesting closer to us than opponent; avoid huge negatives.
            swing = (do - ds) * 10 - ds
            if ds == 0:
                swing += 10000
            if swing > best_res:
                best_res = swing
        # Additional tie-break: avoid walking into the opponent when contests are similar.
        opp_sep = cheb(nx, ny, ox, oy)
        v = best_res + 0.5 * opp_sep
        if v > bestv:
            bestv = v; best = (dx, dy)

    return [best[0], best[1]]