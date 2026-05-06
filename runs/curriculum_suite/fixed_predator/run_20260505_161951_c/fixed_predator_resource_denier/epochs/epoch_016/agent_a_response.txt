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

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            v = d * 1000 - (abs(nx - (w - 1)) + abs(ny - (h - 1)))
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    res_set = set((a, b) for a, b in resources)
    oppd = cheb(x, y, ox, oy)

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in res_set:
            v = 10**9 - 10 * cheb(nx, ny, ox, oy)
        else:
            d_self = cheb(nx, ny, ox, oy)
            # maximize contest advantage against opponent while drifting toward resources
            min_res_self = 10**9
            min_res_opp = 10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                if ds < min_res_self:
                    min_res_self = ds
                do = cheb(ox, oy, rx, ry)
                if do < min_res_opp:
                    min_res_opp = do
            # prefer moves that reduce distance to a resource and increase opponent's urgency
            v = (min_res_opp - min_res_self) * 50 + (d_self - oppd) * 10 - (nx + ny) * 0.001

        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]
    return best