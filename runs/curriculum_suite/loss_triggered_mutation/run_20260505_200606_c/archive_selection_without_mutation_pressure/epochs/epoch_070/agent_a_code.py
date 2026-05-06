def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    best_opp_d = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = cheb(ox, oy, rx, ry)
        if best_opp_d is None or d < best_opp_d or (d == best_opp_d and (rx + ry) < (target[0] + target[1])):
            best_opp_d = d
            target = (rx, ry)

    if target is None:
        return [0, 0]
    tx, ty = target

    best = None
    best_dxdy = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # backup distance to any resource (closer is better)
        backup_d = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d2 = cheb(nx, ny, rx, ry)
            if backup_d is None or d2 < backup_d:
                backup_d = d2

        key = (our_d, -opp_d if opp_d is not None else 0, backup_d if backup_d is not None else 10**9, (nx, ny))
        if best is None or key < best:
            best = key
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]