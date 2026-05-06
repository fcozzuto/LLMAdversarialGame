def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((a, b) for a, b in obstacles)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Want resources we can reach no later than opponent; tie-break for closer and higher leverage
            v = (od - sd) * 1000 - sd
            # small deterministic bias toward upper-left to break symmetry
            v -= (rx + ry) * 0.01
            if v > bestv:
                bestv = v
                best = (rx, ry)

        rx, ry = best
        # Choose next move that minimizes distance to target while keeping advantage over opponent
        bestm = (0, 0)
        bestmv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            nds = cheb(nx, ny, rx, ry)
            ndo = cheb(ox, oy, rx, ry)
            adv = (ndo - nds) * 1000 - nds
            # avoid stepping into positions that let opponent trivially close advantage
            opp_close = cheb(nx, ny, ox, oy)
            v = adv - opp_close * 0.02
            # deterministic tie-break
            if v > bestmv or (v == bestmv and (dx, dy) < bestm):
                bestmv = v
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # No resources: head to area that maximizes separation and restricts opponent (deterministic)
    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        dsep = cheb(nx, ny, ox, oy)
        # Prefer increasing distance to bottom-right (break symmetry) and moving away from opponent
        v = dsep * 1000 - (abs(nx - (w - 1)) + abs(ny - (h - 1)))
        if v > bestv or (v == bestv and (dx, dy) < bestm):
            bestv = v
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]