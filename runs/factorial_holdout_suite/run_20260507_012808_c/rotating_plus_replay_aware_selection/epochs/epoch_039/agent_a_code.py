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
        m = 10**9
        for rx, ry in res:
            d = abs(rx - x) + abs(ry - y)
            if d < m:
                m = d
        return m

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        pickup = 1 if (nx, ny) in res_set else 0
        my_d = min_dist(nx, ny)
        # approximate opponent next ability by their current min distance
        opp_d = min_dist(ox, oy)
        # prefer immediate pickup, then winning the race to the closest resource
        val = pickup * 1000000 + (opp_d - my_d) * 2000 - my_d
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move