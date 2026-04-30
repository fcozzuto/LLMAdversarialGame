def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    opp_now = cheb(sx, sy, ox, oy)

    def nearest_res_dist(x, y):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    # Prefer capturing resources: highest priority.
    # Secondary: keep distance from opponent.
    # Tertiary: move that reduces distance to nearest resource.
    best_move = (0, 0, sx, sy)
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        dres = nearest_res_dist(nx, ny)
        on_res = (nx, ny) in obstacles is False and (nx, ny) in set(resources)
        oppd = cheb(nx, ny, ox, oy)
        # score: capture > approach resource > distance from opponent
        score = 0
        if on_res:
            score += 10**7
        score += -3.0 * dres
        score += 0.5 * oppd
        # small tie-break to avoid aimless oscillation: prefer not decreasing opp distance too much
        score += 0.1 * (oppd - opp_now)
        # deterministic tie-break: lexicographic on (dx,dy)
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]