def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list}
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_next = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid_next.append((dx, dy, nx, ny))
    if not valid_next:
        return [0, 0]
    valid_resources = []
    for p in resources:
        rx, ry = p[0], p[1]
        if inb(rx, ry) and (rx, ry) not in obstacles:
            valid_resources.append((rx, ry))
    if not valid_resources:
        return [0, 0]

    best_move = None
    best_key = None
    for dx, dy, nx, ny in valid_next:
        # Evaluate by the resource we can reach with maximum relative advantage.
        # Key: first prefer resources where we are not later than opponent, then maximize (opp_dist - our_dist),
        # then minimize our distance.
        local_best = None
        for rx, ry in valid_resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            is_adv = 0 if sd <= od else 1
            key = (is_adv, -(od - sd), sd, rx, ry)
            if local_best is None or key < local_best:
                local_best = key
        if best_key is None or local_best < best_key:
            best_key = local_best
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]