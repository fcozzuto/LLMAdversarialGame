def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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
            v = cheb(nx, ny, ox, oy) * 1000 - (abs(nx - (w - 1)) + abs(ny - (h - 1)))
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        min_self = 10**9
        min_opp = 10**9
        best_margin = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd < min_self: min_self = sd
            if od < min_opp: min_opp = od
            margin = (od - sd)
            threat = -2 * margin if od < sd else 0  # penalize picking targets opponent is closer to
            v = margin * 100 - sd + threat
            if v > best_margin:
                best_margin = v

        # Encourage breaking ties by pushing toward targets you can reach first,
        # and also keep some distance from the opponent.
        vtotal = best_margin + (min_opp - min_self) * 10 + cheb(nx, ny, ox, oy) * 1 - (nx + ny) * 0.01
        if vtotal > bestv or (vtotal == bestv and (dx, dy) < (best[0], best[1])):
            bestv = vtotal
            best = [dx, dy]

    return best