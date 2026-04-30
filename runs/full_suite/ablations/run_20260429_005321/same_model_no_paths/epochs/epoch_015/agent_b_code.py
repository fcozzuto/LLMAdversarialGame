def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    if any(sx == rx and sy == ry for rx, ry in res):
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource_target():
        best = None
        best_key = None
        for rx, ry in res:
            d = cheb(sx, sy, rx, ry)
            if best is None or d < best_key[0] or (d == best_key[0] and (rx, ry) < best_key[1]):
                best = (rx, ry)
                best_key = (d, (rx, ry))
        return best

    target = best_resource_target()
    best_score = None
    best_move = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if target is not None:
            rx, ry = target
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            score = (op_d - my_d) * 100 - my_d
        else:
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            cx, cy = corners[0]
            best = None
            for tx, ty in corners:
                d = cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)
                if best is None or d > best:
                    best = d
                    cx, cy = tx, ty
            score = best

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]