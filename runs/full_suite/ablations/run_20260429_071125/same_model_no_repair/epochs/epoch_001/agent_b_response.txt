def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_to = []
    for rx, ry in resources:
        opp_to.append(cheb(ox, oy, rx, ry))

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            cand.append((dx, dy, nx, ny))

    if not cand:
        return [0, 0]

    if resources:
        best = None
        for dx, dy, nx, ny in cand:
            best_adv = -10**9
            min_dist = 10**9
            for i, (rx, ry) in enumerate(resources):
                d = cheb(nx, ny, rx, ry)
                if d < min_dist:
                    min_dist = d
                adv = opp_to[i] - d
                if adv > best_adv:
                    best_adv = adv
            value = best_adv * 7 - min_dist
            if best is None or value > best[0]:
                best = (value, dx, dy)
            elif value == best[0]:
                if (dx, dy) < (best[1], best[2]):
                    best = (value, dx, dy)
        return [int(best[1]), int(best[2])]
    else:
        best = None
        for dx, dy, nx, ny in cand:
            dc = abs(nx - cx) + abs(ny - cy)
            do = cheb(nx, ny, ox, oy)
            value = -dc + 0.2 * do
            if best is None or value > best[0]:
                best = (value, dx, dy)
            elif value == best[0]:
                if (dx, dy) < (best[1], best[2]):
                    best = (value, dx, dy)
        return [int(best[1]), int(best[2])]