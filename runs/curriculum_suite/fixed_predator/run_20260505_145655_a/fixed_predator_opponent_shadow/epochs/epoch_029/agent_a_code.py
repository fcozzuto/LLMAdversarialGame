def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best = None
    best_key = None
    for tx, ty in resources:
        me_d = abs(tx - x) + abs(ty - y)
        opp_d = abs(tx - ox) + abs(ty - oy)
        # prefer becoming ahead on the target; tie-break by smaller me distance then farther opp distance
        key = (opp_d - me_d, -me_d, opp_d, -(tx + ty))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    tx_dx = sign(tx - x)
    ty_dy = sign(ty - y)
    desired = (x + tx_dx, y + ty_dy)

    # Try moves that don't hit obstacles, prioritizing those that reduce distance to target.
    best_m = None
    best_m_key = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        me_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)
        lead = opp_d - me_d
        # Prefer: keep or improve lead, then closer to target, then closer to desired direction.
        dir_match = -((dx - tx_dx) * (dx - tx_dx) + (dy - ty_dy) * (dy - ty_dy))
        key = (lead, -me_d, dir_match, -(nx + 3 * ny))
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]