def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
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

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    tx, ty = (w - 1, h - 1)
    if not resources:
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            d_opp = cheb(nx, ny, ox, oy)
            prog = -(abs(nx - tx) + abs(ny - ty))
            v = d_opp * 1000 + prog
            if v > bestv:
                bestv = v; best = [dx, dy]
        return [best[0], best[1]]

    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        my_progress = -md(nx, ny, tx, ty)
        best_gain = -10**18
        worst_deny = 10**18
        for rx, ry in resources:
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            # Prefer resources where we are closer than the opponent (gain),
            # and deter/deny where they are closer (deny).
            gain = (d_opp - d_self) * 20 - cheb(nx, ny, rx, ry)
            if gain > best_gain:
                best_gain = gain
            deny = (d_self - d_opp) * 12 - cheb(nx, ny, rx, ry)
            if deny < worst_deny:
                worst_deny = deny

        # Also discourage stepping into states where opponent can instantly reach many options
        opp_pressure = 0
        for rx, ry in resources:
            opp_pressure += 1 if cheb(ox, oy, rx, ry) <= 1 else 0

        v = best_gain + my_progress + min(0, worst_deny) * 1.5 - opp_pressure * 0.5
        if v > bestv:
            bestv = v; best = [dx, dy]

    return [best[0], best[1]]