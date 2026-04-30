def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Prefer moving toward closest resource if safe; otherwise head to a corner that minimizes distance to center while avoiding opponent.
    if resources:
        best = None
        bestv = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # distance to nearest resource after move
            dmin = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            # reduce score if moving onto opponent
            fear = 0
            if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
                fear = 5
            v = dmin - fear
            if v < bestv:
                bestv = v
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # If no resources or no good move toward resources, try to move away from opponent while staying legal.
    best = (0, 0)
    bestv = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist_opp = cheb(nx, ny, ox, oy)
        dist_goal = 0
        # prefer increasing distance from opponent
        v = dist_opp * -1
        # small bias to not stay if stuck
        if dx == 0 and dy == 0:
            v -= 0.1
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]