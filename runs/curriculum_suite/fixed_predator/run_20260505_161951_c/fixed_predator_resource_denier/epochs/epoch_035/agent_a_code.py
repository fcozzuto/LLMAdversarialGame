def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1, h - 1
        bestd = -10**18
        best = (0, 0)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            # drift away from opponent while not straying too far from goal corner
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 50 - (abs(tx - nx) + abs(ty - ny))
            if v > bestd or (v == bestd and (dx, dy) < best):
                bestd = v
                best = (dx, dy)
        return [best[0], best[1]]

    bestv = -10**18
    best = (0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        self_d = cheb(nx, ny, x, y)  # always 0 or 1-ish; keeps tie-breaking stable
        v = -self_d
        # evaluate best/worst target pressure for this step
        for rx, ry in resources:
            self_to = cheb(nx, ny, rx, ry)
            opp_to = cheb(nx, ny, ox, oy) + cheb(ox, oy, rx, ry) - cheb(nx, ny, ox, oy)
            # main: prefer cells that make us closer than opponent to some resource
            delta = opp_to - self_to
            # secondary: prefer getting nearer to the resource we most likely win
            prox = -(self_to)
            # avoid suicidal clustering: if opponent is about to beat many, shift away slightly
            v = max(v, delta * 120 + prox * 3 + (0 if (rx == nx and ry == ny) else -1))
        # small deterministic nudge: bias toward increasing x then y
        v += (nx * 0.01 + ny * 0.001)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]