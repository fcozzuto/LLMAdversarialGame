def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {tuple(p) for p in obstacles_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a target that we can reach no later than the opponent; otherwise pick closest to us.
    best = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        if my_d <= op_d:
            key = (0, my_d, rx, ry)  # smallest my_d among "not slower"
        else:
            # when behind everywhere, pick smallest my_d, tie by smaller (my_d - op_d)
            key = (1, my_d, my_d - op_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Choose move that maximizes our advantage to this target while avoiding obstacles.
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        my_d2 = dist(nx, ny, tx, ty)
        op_d2 = dist(ox, oy, tx, ty)
        slack = op_d2 - my_d2  # higher is better
        # Prefer advancing (smaller my_d2), also discourage positions adjacent to obstacles to reduce accidental hits.
        adj_pen = 0
        for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx-1, ny+1), (nx+1, ny-1), (nx+1, ny+1)):
            if inb(ax, ay) and (ax, ay) in obstacles:
                adj_pen += 1
        val = (-(slack), my_d2, adj_pen, dx, dy)  # minimize negative slack => maximize slack
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move