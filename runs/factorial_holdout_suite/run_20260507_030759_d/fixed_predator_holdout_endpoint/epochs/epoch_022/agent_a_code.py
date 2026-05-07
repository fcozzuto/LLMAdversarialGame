def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b, c, d2):
        return abs(a - c) + abs(b - d2)

    def nearest_dist(x, y):
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dv = d(x, y, rx, ry)
            if best is None or dv < best:
                best = dv
        return best if best is not None else None

    best = None  # (primary, secondary, tertiary, dx, dy)
    target = (w // 2, h // 2)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_nd = nearest_dist(nx, ny)
        opp_nd = nearest_dist(ox, oy)
        if my_nd is None or opp_nd is None:
            my_d = d(nx, ny, target[0], target[1])
            opp_d = d(ox, oy, target[0], target[1])
            primary = opp_d - my_d
            secondary = my_d
            tertiary = d(nx, ny, ox, oy)
        else:
            primary = opp_nd - my_nd
            secondary = my_nd
            tertiary = d(nx, ny, ox, oy)

        cand = (primary, -secondary, -tertiary, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[3], best[4]]