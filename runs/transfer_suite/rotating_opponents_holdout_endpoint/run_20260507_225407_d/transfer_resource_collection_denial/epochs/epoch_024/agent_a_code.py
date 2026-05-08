def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except Exception:
            pass
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = None
    best = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - myd
        key = (adv, -myd, -rx, -ry)
        if best is None or key > best:
            best = key
            best_target = (rx, ry)

    if best_target is None:
        best_target = resources[0]
    tx, ty = best_target

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= gw or ny >= gh:
            continue
        if (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - myd
        score = (adv, -myd, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]