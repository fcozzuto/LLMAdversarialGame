def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        my_best = 10**9
        opp_best_for_these = 10**9
        immediate = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                immediate = 1
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > (opp_best_for_these - my_best):
                my_best = myd
                opp_best_for_these = opd

        # Heuristic: win the race (maximize opd - myd), then minimize myd, then prefer center, then prefer reducing dx^2+dy^2-ish toward resources.
        center = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        race = (opp_best_for_these - my_best)
        key = (immediate, race, -my_best, center, -(abs(nx - ox) + abs(ny - oy)))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move