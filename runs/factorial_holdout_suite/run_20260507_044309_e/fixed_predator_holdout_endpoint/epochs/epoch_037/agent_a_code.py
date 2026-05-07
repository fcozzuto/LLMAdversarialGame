def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best = -10**18
        opp_best = 10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Prefer resources we are strictly faster at; if none, reduce opponent's advantage.
            gain = (oppd - myd) * 1000 - myd
            if myd <= oppd:
                gain += 5000
            my_best = max(my_best, gain)
            opp_best = min(opp_best, oppd - myd)

        # Secondary tie-break: move that also keeps us close to nearest resource overall.
        nearest = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        wall_push = 0
        if nx in (0, w - 1) or ny in (0, h - 1):
            wall_push = -1  # slight preference to avoid edge trapping

        score = my_best + opp_best * 10 - nearest + wall_push
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]