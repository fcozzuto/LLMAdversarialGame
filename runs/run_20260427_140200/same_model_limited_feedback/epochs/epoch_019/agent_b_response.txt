def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    def center_move():
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_c = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obstacles:
                continue
            c = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            if best_c is None or c < best_c:
                best_c, best = c, [dx, dy]
        return best if best is not None else [0, 0]

    if not resources:
        return center_move()

    best_move = [0, 0]
    best_cost = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        ds = (nx, ny)
        cur_cost = None
        for rx, ry in resources:
            r = (rx, ry)
            d1 = dist(ds, r)
            d2 = dist((ox, oy), r)
            lead = d2 - d1
            target_cost = d1 + 0.10 * d2 - 1.50 * (lead if lead > 0 else 0) + (0.75 if lead < 0 else 0)
            if cur_cost is None or target_cost < cur_cost:
                cur_cost = target_cost
        if cur_cost is None:
            continue
        if best_cost is None or cur_cost < best_cost:
            best_cost, best_move = cur_cost, [dx, dy]

    return best_move