def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - sd  # positive means we are no slower
            key = (0 if gap <= 0 else 1, -gap, sd, rx, ry)  # prefer not slower; then biggest gap; then closest
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        if best is None:
            return (w - 1) // 2, (h - 1) // 2
        return best

    tx, ty = best_target()
    preferred = (0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    px, py = sx + preferred[0], sy + preferred[1]
    if valid(px, py):
        return [preferred[0], preferred[1]]

    best_move = None
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        my_gap = opp_d - my_d
        # steer to reduce our distance; also keep gap positive if possible; deterministic tie-break
        key = (0 if my_gap <= 0 else 1, -my_gap, my_d, nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]