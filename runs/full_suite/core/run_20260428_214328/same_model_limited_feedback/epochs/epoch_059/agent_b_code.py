def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # fallback: move away from opponent to avoid contact and toward center
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_ctr = cheb(nx, ny, tx, ty)
            v = (d_opp, -d_ctr)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # choose resource we are likely to reach first, favoring being ahead
    best_res = None
    best_sc = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # lower is better for our move; being ahead is strongly rewarded
        sc = (d_self - d_opp * 1.05, d_self, -rx, -ry)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_res = (rx, ry)

    rx, ry = best_res
    # prefer step that reduces Chebyshev distance to chosen resource
    best = (0, 0)
    best_dist = None
    best_tie = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, rx, ry)
        # tie-break: also maximize distance from opponent to reduce their contest
        d_opp = cheb(nx, ny, ox, oy)
        tie = (-d_opp, -nx, -ny)
        if best_dist is None or (d < best_dist) or (d == best_dist and tie > best_tie):
            best_dist = d
            best_tie = tie
            best = (dx, dy)

    return [int(best[0]), int(best[1])]