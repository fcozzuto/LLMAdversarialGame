def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width")
    h = observation.get("grid_height")
    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = obs_list if isinstance(obs_list, set) else set(tuple(p) for p in obs_list)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    targets = []
    for r in res:
        rx, ry = r
        if (rx, ry) not in obstacles:
            targets.append((rx, ry))
    if not targets:
        return [0, 0]

    best = None
    bd = None
    for rx, ry in targets:
        d = cheb(sx, sy, rx, ry)
        if best is None or d < bd or (d == bd and (rx, ry) < best):
            best = (rx, ry)
            bd = d

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    curd = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if w is not None and (nx < 0 or nx >= w): 
            continue
        if h is not None and (ny < 0 or ny >= h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        score = (od - nd, -(nd), -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)), -abs(dx) - abs(dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if cheb(sx + best_move[0], sy + best_move[1], tx, ty) > curd:
        return [0, 0]
    return best_move