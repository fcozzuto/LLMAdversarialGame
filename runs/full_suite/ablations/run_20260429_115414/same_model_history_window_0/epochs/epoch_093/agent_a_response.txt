def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    def cheb(a, b, c, d):
        adx = a - c
        bd = b - d
        if adx < 0: adx = -adx
        if bd < 0: bd = -bd
        return adx if adx >= bd else bd

    # If no resources, head toward center to improve future chances.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = None
        for dx, dy in candidates:
            nx, ny = x + dx, y + dy
            dist = abs(nx - cx) + abs(ny - cy)
            if best is None or dist < bestv:
                bestv = dist
                best = (dx, dy)
        return [best[0], best[1]]

    # Objective: get a resource while keeping opponent farther (deny/tempo).
    best = candidates[0]
    bestv = None
    for dx, dy in candidates:
        nx, ny = x + dx, y + dy
        my_to_center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        worst_case = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gap = do - ds  # positive means we are closer than opponent
            # Prefer also closer absolute distance; slight center preference breaks ties.
            v = 3.0 * gap - 0.15 * ds - 0.01 * my_to_center
            if worst_case is None or v > worst_case:
                worst_case = v
        if bestv is None or worst_case > bestv:
            bestv = worst_case
            best = (dx, dy)
    return [best[0], best[1]]