def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_res_dist(x, y):
        if not resources:
            return 10**9
        m = 10**9
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if d < m:
                m = d
        return m

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dres = best_res_dist(nx, ny)
        dopp = abs(nx - ox) + abs(ny - oy)
        key = (dres, -dopp, dx, dy)  # prioritize closest resource, then farther from opponent
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]