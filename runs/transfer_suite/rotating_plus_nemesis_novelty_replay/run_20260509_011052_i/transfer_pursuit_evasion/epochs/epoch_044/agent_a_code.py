def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)
        m = mobility(nx, ny)

        # tie-breaks: resources for pursuer, away-from-resources for evader (if any)
        if resources:
            d_res = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        else:
            d_res = 0

        if pursuer:
            # primary: smaller distance to opponent
            v = -d_op * 1000 + m * 3
            if resources:
                v -= d_res * 2
        else:
            # primary: larger distance from opponent
            v = d_op * 1000 + m * 3
            if resources:
                v += d_res * 1  # keep away if resources exist

        # deterministic tie-break: prefer staying only if equal, else smallest (dx,dy) lex
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]