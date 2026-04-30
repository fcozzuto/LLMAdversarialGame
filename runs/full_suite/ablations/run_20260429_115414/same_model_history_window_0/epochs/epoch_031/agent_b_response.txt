def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obstacle_set = set((int(x), int(y)) for x, y in obstacles if 0 <= int(x) < w and 0 <= int(y) < h)

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_resource = None
    best_val = None
    for rx, ry in resources:
        rx = int(rx); ry = int(ry)
        if (rx, ry) in obstacle_set:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = (do - ds) * 10 - ds
        if best_val is None or val > best_val:
            best_val = val
            best_resource = (rx, ry)

    if best_resource is None:
        return [0, 0]
    tx, ty = best_resource

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacle_set:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        score = (-d_to_t, d_to_o, -abs(nx - w // 2) - abs(ny - h // 2))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]