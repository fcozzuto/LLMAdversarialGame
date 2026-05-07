def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    def nearest_dist(px, py):
        best = None
        for rx, ry in res:
            d = abs(px - rx) + abs(py - ry)
            if best is None or d < best:
                best = d
        return best

    if not res:
        best = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                d = abs(nx - ox) + abs(ny - oy)
                score = (d, -dx, -dy)
                if best is None or score > best:
                    best = score
                    bd = (dx, dy)
        return [bd[0], bd[1]] if best is not None else [0, 0]

    my_d0 = nearest_dist(x, y)
    best = None
    bd = (0, 0)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (in_bounds(nx, ny) and (nx, ny) not in obstacles):
            continue
        my_dn = nearest_dist(nx, ny)
        opp_dn = abs(ox - nx) + abs(oy - ny)
        centerx, centery = (gw - 1) // 2, (gh - 1) // 2
        to_center = abs(nx - centerx) + abs(ny - centery)
        score = (-my_dn, opp_dn, -to_center, -dx, -dy)
        if best is None or score > best:
            best = score
            bd = (dx, dy)

    return [bd[0], bd[1]] if best is not None else [0, 0]