def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    def infty_cell_score(cx, cy):
        # Higher is better for us: prefer cells that are closer to us than opponent.
        return cheb(ox, oy, cx, cy) - cheb(x, y, cx, cy)

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            # tie-break to a stable corner-ish drift
            v = d * 1000 - (abs(nx - (w - 1)) + abs(ny - (h - 1)))
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    # Choose the most favorable resource by "denial margin"
    # Prefer resources that opponent is not close to while we are closer.
    best_res = resources[0]
    best_rv = -10**18
    for rx, ry in resources:
        rv = cheb(ox, oy, rx, ry) - cheb(x, y, rx, ry)
        # mild preference for nearer resources to reduce tie chaos
        rv = rv * 10 - cheb(x, y, rx, ry)
        if rv > best_rv or (rv == best_rv and (rx, ry) < (best_res[0], best_res[1])):
            best_rv = rv
            best_res = [rx, ry]

    tx, ty = best_res

    # Move to reduce chebyshev distance to the chosen target while keeping denial good.
    best_move = [0, 0]
    best_mv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        d0 = cheb(x, y, tx, ty)
        # denial value improvement if we step toward target but away from opponent
        denial = infty_cell_score(tx, ty)
        # also consider opponent closeness to our landing cell (lower is better for opponent)
        opp_to_land = cheb(nx, ny, ox, oy)
        v = (d0 - d1) * 1000 + denial * 10 - opp_to_land
        if v > best_mv or (v == best_mv and (dx, dy) < (best_move[0], best_move[1])):
            best_mv = v
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]