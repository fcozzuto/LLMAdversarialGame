def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    res = observation.get("resources", [])
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    def cell_blocked(x, y):
        return (x, y) in obs

    # Choose target resource: prefer nearer to self, farther from opponent
    if res:
        best_t = None
        best_key = None
        for tx, ty in res:
            ds = dist((sx, sy), (tx, ty))
            do = dist((ox, oy), (tx, ty))
            # Lower is better; slight bias to reduce risk of opponent stealing
            key = (ds - 0.35 * do, ds, -do, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty)
        tx, ty = best_t
        # If adjacent, move onto it (or stay if already there)
        cur_has = (sx, sy) == (tx, ty)

        best_move = (0, 0)
        best_cost = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if cell_blocked(nx, ny):
                continue
            if (nx, ny) == (tx, ty):
                cost = -10  # strongly prefer resource
            else:
                cost = dist((nx, ny), (tx, ty))
                # mild deterrent: avoid stepping into opponent-strong area
                cost += 0.08 * dist((nx, ny), (ox, oy))
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: drift toward center while avoiding obstacles
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_cost = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if cell_blocked(nx, ny):
            continue
        dc = abs(nx - cx) + abs(ny - cy)
        cost = dc
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]