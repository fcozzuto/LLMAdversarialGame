def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    center_bias = -(abs(sx - cx) + abs(sy - cy))

    # Pick a deterministic best resource: prefer we arrive first; then nearer; then center.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        tempo = oppd - myd  # positive => we arrive earlier
        if tempo < 0:
            continue  # commit to contestable resources to beat edge patrol
        cent = -(abs(rx - cx) + abs(ry - cy))
        # Slightly prefer targets that are also far from opponent (more control).
        opp_far = man(ox, oy, rx, ry)
        key = (-tempo, myd, -opp_far, cent, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    # If nothing contestable, take the "least bad" resource we can reach sooner or tie.
    if best is None:
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(sx, sy, rx, ry)
            oppd = man(ox, oy, rx, ry)
            tempo = oppd - myd
            cent = -(abs(rx - cx) + abs(ry - cy))
            key = (tempo * 10, myd, -cent, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)

    tx, ty = best if best is not None else (cx, cy)

    # Choose move by maximizing progress to target while keeping safe vs obstacles and not getting trapped.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_to_o = man(nx, ny, ox, oy)
        # Progress + slight distance from opponent (helps contest/avoid edge sweep).
        score = (-d_to_t, d_to_o, -(abs(nx - cx) + abs(ny - cy)), center_bias - d_to_t)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]