def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    selfp0 = (sx, sy)
    oppp = (ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        selfp = (nx, ny)

        best_self_d = 10**9
        best_gain = -10**9
        nearest_r = None

        for r in resources:
            sd = cheb(selfp, r)
            od = cheb(oppp, r)
            if sd < best_self_d:
                best_self_d = sd
                nearest_r = r
            gain = od - sd  # positive means self closer than opponent to this resource
            if gain > best_gain:
                best_gain = gain

        # Secondary: move toward the resource that benefits most; tie-break deterministically
        if nearest_r is None:
            nearest_r = resources[0]
        sx_goal = cheb(selfp, nearest_r)
        ox_goal = cheb(oppp, nearest_r)

        # Big weight to positive advantage; then minimize own distance; then favor reducing opponent distance
        key = (-(best_gain + 10) * 10_000, best_self_d, ox_goal - sx_goal, dx, dy, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]