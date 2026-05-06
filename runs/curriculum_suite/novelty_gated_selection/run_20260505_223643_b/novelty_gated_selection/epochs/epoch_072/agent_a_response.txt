def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def mdists(x, y):
        best_d = None
        for rx, ry in resources:
            d = (rx - x) * (rx - x) + (ry - y) * (ry - y)
            if best_d is None or d < best_d:
                best_d = d
        return best_d if best_d is not None else 10**18

    opp_best = mdists(ox, oy)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_best = mdists(nx, ny)

        # Primary: maximize (opponent_closest_dist - our_closest_dist)
        adv = opp_best - self_best

        # Secondary: prefer moves that reduce our distance and keep opponent from getting closer.
        # (Approximate with how our move would change relative closeness to resources.)
        closest_res = resources[0]
        self_d_sq = None
        for rx, ry in resources:
            d = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
            if self_d_sq is None or d < self_d_sq:
                self_d_sq = d
                closest_res = (rx, ry)

        ox_d_sq = (closest_res[0] - ox) * (closest_res[0] - ox) + (closest_res[1] - oy) * (closest_res[1] - oy)
        # If we can get closer to a resource than opponent, it gets a boost.
        contest = ox_d_sq - self_d_sq

        # Tertiary: avoid stepping into the opponent immediate neighborhood.
        opp_near = max(abs(nx - ox), abs(ny - oy))

        score = (adv, contest, -self_best, -opp_near, dx, dy)
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move if best is not None else [0, 0]