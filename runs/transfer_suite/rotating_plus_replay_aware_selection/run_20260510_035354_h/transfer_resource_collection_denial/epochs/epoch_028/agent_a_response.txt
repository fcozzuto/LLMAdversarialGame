def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def min_to_resources(x, y):
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    my_best_move = (0, 0)
    best_obj = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_min = min_to_resources(nx, ny)

        # Predict opponent greedy step toward their nearest resource.
        op_best = 10**9
        op_nx, op_ny = ox, oy
        for odx, ody in moves:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            d = min_to_resources(tx, ty)
            if d < op_best:
                op_best = d
                op_nx, op_ny = tx, ty

        # Prefer smaller my_min and larger opponent distance after their step.
        obj = (op_best - my_min)
        # Mild tie-break: prefer moves that also reduce direct distance to nearest resource.
        if obj > best_obj:
            best_obj = obj
            my_best_move = (dx, dy)
        elif obj == best_obj:
            if min_to_resources(nx, ny) < min_to_resources(sx + my_best_move[0], sy + my_best_move[1]):
                my_best_move = (dx, dy)

    return [int(my_best_move[0]), int(my_best_move[1])]