def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set(tuple(p) for p in obstacles)
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    if not resources:
        return [0, 0]
    best_t = None
    best_key = None
    for r in resources:
        rx, ry = r
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = r
    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        self_to = man((nx, ny), (tx, ty))
        opp_to = man((ox, oy), (tx, ty))
        key = (opp_to - self_to, -self_to, -dx, -dy, nx, ny)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]