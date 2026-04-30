def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs.add((int(o[0]), int(o[1])))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if (x, y) in obs:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    if not res:
        tx, ty = (w - 1, h - 1) if cheb(x, y, 0, 0) < cheb(ox, oy, 0, 0) else (0, 0)
    else:
        best = None
        for rx, ry in res:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # prefer resources you can reach earlier; break ties by absolute proximity
            key = (od - sd, -(sd + 2 * abs(rx - ox) + 2 * abs(ry - oy)), -rx - ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    best_move = (None, -10**9)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # relative advantage after this move
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        advantage = (opp_d - self_d)
        # small preference to move closer to target
        advantage -= 0.1 * self_d
        # avoid stepping away if already on a good route
        if (x, y) != (nx, ny):
            advantage += 0.02 * cheb(x, y, tx, ty) * (1 if self_d < cheb(x, y, tx, ty) else -1)
        if advantage > best_move[1]:
            best_move = ((dx, dy), advantage)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]