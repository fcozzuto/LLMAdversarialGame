def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_value(nx, ny):
        if not resources:
            return 0
        # Choose target based on who reaches first from (nx,ny) vs opponent.
        # Positive means we are closer (can contest/collect first).
        best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd
            # Prefer nearer targets when margins equal; also slightly prefer cells that
            # increase the opponent's distance to their closest resource (denial).
            if sd < 1000:
                opp_closest = 10**9
                for tx, ty in resources:
                    d = cheb(ox, oy, tx, ty)
                    if d < opp_closest:
                        opp_closest = d
                val = margin * 100 + (-sd) * 2 + (opp_closest * 0)  # keep deterministic
            else:
                val = -sd
            if val > best:
                best = val
        # Denial term: move to increase opponent's nearest-resource distance.
        opp_near = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        my_near = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        best += (my_near == 0) * 50
        best += (opp_near - cheb(ox, oy, nx, ny)) * 0  # stable tie-break base
        return best

    # If no resources, drift away from opponent while keeping options open.
    if not resources:
        best_move = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            # also keep away from borders a bit
            border = min(nx, ny, w - 1 - nx, h - 1 - ny)
            v = d_opp * 100 - (7 - border)
            if v > bestv or (v == bestv and (dx, dy) < best_move):
                bestv = v
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Otherwise: evaluate each legal move by best achievable contest margin, with
    # a small penalty for moving closer to obstacles (via immediate legality only).
    best_move = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        v = best_value(nx, ny)
        # tiny bias: prefer moves that are not dominated by immediate opponent distance
        v += (cheb(nx, ny, ox, oy) - cheb(x, y, ox, oy)) * 0.5
        if v > bestv or (v == bestv and (dx, dy) < best_move):
            bestv = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]