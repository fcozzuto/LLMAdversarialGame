def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    blocked = obstacles

    # If no resources, move toward center-ish to reduce distance to future resources
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in blocked: 
                continue
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            score = d
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose target resource: closest with tie-break favoring far-from-opponent (to contest)
    def sqdist(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    best_res = None
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        myd = sqdist((sx, sy), (rx, ry))
        opd = sqdist((ox, oy), (rx, ry))
        # Prefer smaller myd; if tie, prefer larger opd (make opponent take longer)
        key = (myd, -opd, rx, ry)
        if best_res is None or key < best_res[0]:
            best_res = (key, (rx, ry))
    tx, ty = best_res[1]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # If already on a resource, move to the next closest resource deterministically by minimizing sum of distances
    if (sx, sy) == (tx, ty):
        best_next = None
        for rx, ry in resources:
            if (rx, ry) in blocked: 
                continue
            k = (sqdist((sx, sy), (rx, ry)), -sqdist((ox, oy), (rx, ry)), rx, ry)
            if best_next is None or k < best_next[0]:
                best_next = (k, (rx, ry))
        tx, ty = best_next[1]

    # Evaluate each legal move by distance to target and "escape" from opponent if both would reduce distance too much
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        myd = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        opd = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # Penalties: avoid moving closer to opponent too aggressively when target is near
        # Reward: keep distance from opponent for contesting nearby resources
        penalty = 0
        if opd < 9:  # within 3 steps
            penalty += (9 - opd)

        # Small tie-break by prefer straight moves earlier deterministically
        straight_bias = 1 if dx == 0 or dy == 0 else 0
        key = (myd + penalty, -opd, -straight_bias, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]