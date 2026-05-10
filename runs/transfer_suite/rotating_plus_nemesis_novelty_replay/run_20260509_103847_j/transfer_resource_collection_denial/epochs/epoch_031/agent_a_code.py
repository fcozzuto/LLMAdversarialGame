def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Prefer a deterministic "territory swing" toward resources we are currently closer to.
    closer = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if sd < od:
            closer.append((rx, ry, od - sd))  # bigger margin => stronger claim

    if closer:
        # Weighted centroid (weights are deterministic, no randomness)
        totw = 0
        tx_num = 0
        ty_num = 0
        for rx, ry, m in closer:
            wgt = 1 + (m if m > 0 else 0)
            totw += wgt
            tx_num += rx * wgt
            ty_num += ry * wgt
        tx = tx_num // totw
        ty = ty_num // totw
    else:
        # If we aren't ahead anywhere, chase the best swing resource by margin, then head toward its direction.
        best = None
        best_key = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Maximize (od - sd): we want the largest "we're less behind" situation
            key = (-(od - sd), sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if valid(nx, ny) and (nx, ny) != (ox, oy):
        return [dx, dy]

    # Deterministic fallback: try the 8-neighborhood toward the target, then toward staying put.
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_dist = None
    for mdx, mdy in moves:
        mx, my = sx + mdx, sy + mdy
        if not valid(mx, my):
            continue
        if (mx, my) == (ox, oy):
            continue
        d = man(mx, my, tx, ty)
        if best_dist is None or d < best_dist or (d == best_dist and (mdx, mdy) < tuple(best_move)):
            best_dist = d
            best_move = [mdx, mdy]
    return best_move