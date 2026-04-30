def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obs_list = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obs_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid_pos(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res_list = observation.get("resources") or []
    resources = [(int(p[0]), int(p[1])) for p in res_list]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (do - ds, -ds, -ry, -rx)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = ox, oy

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_pos(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        score = (do - ds) * 1000 - ds
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]