def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if valid(nx, ny) and (ddx, ddy) == (dx, dy):
                return [ddx, ddy]
        return [0, 0]

    best_move = (0, 0)
    best_score = None
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        # Advantage: prefer moving to states where we can reach some resource sooner than opponent.
        adv_best = None
        for tx, ty in resources:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = (od - sd) * 10 - sd  # large weight on winning race, tie-break by speed
            if adv_best is None or adv > adv_best:
                adv_best = adv
        # Secondary: break ties by preferring shorter distance to closest resource.
        close = min(cheb(nx, ny, tx, ty) for tx, ty in resources)
        key = (adv_best, -close)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]