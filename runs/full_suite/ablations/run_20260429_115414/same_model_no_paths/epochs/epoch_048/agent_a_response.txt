def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target_pref = sorted(resources, key=lambda p: (p[0] * 100 + p[1]))  # deterministic tiebreak source

    opp_min_d = []
    for rx, ry in resources:
        opp_min_d.append(cheb(ox, oy, rx, ry))

    best_key = None
    best_move = (0, 0)
    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        # Evaluate as "reach advantage" over opponent to the best resource for us.
        self_best = 10**9
        self_arg = (resources[0][0], resources[0][1])
        for i, (rx, ry) in enumerate(resources):
            d = cheb(nx, ny, rx, ry)
            if d < self_best:
                self_best = d
                self_arg = (rx, ry)

        rx, ry = self_arg
        opp_d = cheb(ox, oy, rx, ry)
        # Encourage being strictly closer; also discourage moves that give up too much.
        advantage = opp_d - self_best

        # Secondary: prefer moves that reduce absolute distance and prefer deterministic resource.
        self_abs = self_best
        resource_rank = (rx * 100 + ry)
        key = (advantage, -self_abs, -resource_rank, dxm, dym)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]