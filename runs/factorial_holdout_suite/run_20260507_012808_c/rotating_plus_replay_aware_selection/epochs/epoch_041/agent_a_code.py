def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    res = [tuple(r) for r in resources]
    res_set = set(res)

    def min_dist(x, y):
        md = 10**9
        for rx, ry in res:
            d = abs(rx - x) + abs(ry - y)
            if d < md:
                md = d
        return md

    best_move = [0, 0]
    best_val = -10**18
    opp_min = min_dist(ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_min = min_dist(nx, ny)
        pickup = 1 if (nx, ny) in res_set else 0

        # encourage taking a resource, then getting closer; also prefer moves that outpace opponent
        pace_gain = (opp_min - my_min)
        val = pickup * 10000 + pace_gain * 50 - my_min

        # slight tie-break: move that increases lexicographic toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val += -0.1 * (abs(nx - cx) + abs(ny - cy))

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]