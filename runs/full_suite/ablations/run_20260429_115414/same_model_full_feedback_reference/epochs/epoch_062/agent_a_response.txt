def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not resources:
        for dx, dy in [(-1, -1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        advantage = opd - myd  # positive means we arrive earlier in Chebyshev steps
        key = (-(advantage), myd, rx, ry)  # minimize: (more advantage first => negative; then nearer; then deterministic)
        if best is None or key < best_key:
            best, best_key = (rx, ry), key

    rx, ry = best
    my_best = None
    my_score_best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd2 = cheb(nx, ny, rx, ry)
        opd2 = cheb(ox, oy, rx, ry)
        # prefer reducing our distance; break ties by increasing our lead (advantage).
        lead2 = opd2 - myd2
        score = (-(lead2), myd2, dx, dy)
        if my_best is None or score < my_score_best:
            my_best, my_score_best = (dx, dy), score

    return [int(my_best[0]), int(my_best[1])]