def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    resources = [r for r in resources if r not in obstacles]
    if not resources:
        return [0, 0]

    my_min_d = min(man(sx, sy, rx, ry) for rx, ry in resources)
    op_min_d = min(man(ox, oy, rx, ry) for rx, ry in resources)
    behind = (my_min_d - op_min_d) >= 2

    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if behind:
            # Reduce chance we get stolen: pick targets where opponent is not aggressively closer.
            key = (-(od - sd), sd, cheb(ox, oy, rx, ry), (rx + 31 * ry))
        else:
            # Prefer resources where we are closer (or opponent much farther).
            key = (min(od - sd, 9999), sd, cheb(ox, oy, rx, ry), (rx + 31 * ry))
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    # Avoid stepping into obstacles when possible.
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            # Prefer closeness to target, but break ties by staying ahead of opponent.
            cand_key = (man(nx, ny, tx, ty), man(ox, oy, tx, ty) - man(nx, ny, tx, ty), cheb(nx, ny, tx, ty), mx, my)
            candidates.append((cand_key, mx, my))

    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][1]), int(candidates[0][2])]