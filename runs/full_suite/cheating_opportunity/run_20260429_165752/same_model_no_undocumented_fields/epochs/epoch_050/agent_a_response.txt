def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    opp_dists = {(rx, ry): cheb(ox, oy, rx, ry) for (rx, ry) in resources}

    # Prefer resources we can reach strictly sooner than opponent.
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_d = cheb(nx, ny, nx, ny)  # 0
        if resources:
            ahead = []
            for (rx, ry) in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = opp_dists.get((rx, ry), cheb(ox, oy, rx, ry))
                if d_me < d_op:
                    ahead.append((d_me - d_op, d_me, d_op, rx, ry))
            if ahead:
                ahead.sort()
                key = (0, ahead[0][0], ahead[0][1], ahead[0][2], dx, dy)
            else:
                # No clear lead: minimize our distance and avoid moving closer to opponent.
                if resources:
                    nearest = min(resources, key=lambda r: cheb(nx, ny, r[0], r[1]))
                    key = (1, cheb(nx, ny, nearest[0], nearest[1]), -cheb(nx, ny, ox, oy), dx, dy)
                else:
                    key = (2, cheb(nx, ny, w // 2, h // 2), dx, dy)
        else:
            key = (3, cheb(nx, ny, w // 2, h // 2), dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]