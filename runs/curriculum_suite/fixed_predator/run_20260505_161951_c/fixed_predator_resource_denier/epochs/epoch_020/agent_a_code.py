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

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set((rx, ry) for rx, ry in resources)
    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy) * 1000 - (nx + ny)
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    # Prefer: immediate resource, then resource that opponent is less likely to contest,
    # while making your path denser (pull toward resource "basin" and away from opponent).
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) in res_set:
            bestv_new = 10**9 + cheb(nx, ny, ox, oy) * 10 - (abs(nx - (w - 1)) + abs(ny - (h - 1)))
        else:
            self_d_opp = cheb(nx, ny, ox, oy)
            # Evaluate top few nearby resources only (deterministic, local).
            mind = 10**9
            mind2 = 10**9
            best_gain = -10**18
            for rx, ry in resources:
                d_s = cheb(nx, ny, rx, ry)
                if d_s < mind:
                    mind2 = mind
                    mind = d_s
                elif d_s < mind2:
                    mind2 = d_s
                # Contest metric: resources where you are closer than opponent.
                d_o = cheb(ox, oy, rx, ry)
                gain = (d_o - d_s)
                if gain > best_gain:
                    best_gain = gain
            # Basin favors staying in tight route to a good resource cluster.
            v1 = best_gain * 200 + (mind2 if mind2 < 10**9 else 0) * -20
            v2 = self_d_opp * 5 + (-(nx + ny))  # slight drift toward lower indices for determinism
            bestv_new = v1 + v2 - mind * 50
        if bestv_new > bestv or (bestv_new == bestv and (dx, dy) < (best[0], best[1])):
            bestv = bestv_new
            best = [dx, dy]
    return best