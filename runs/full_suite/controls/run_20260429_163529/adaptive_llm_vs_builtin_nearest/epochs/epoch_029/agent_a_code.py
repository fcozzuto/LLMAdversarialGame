def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best_move = None
    best_score = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Prefer states that reduce our time-to-resource while increasing opponent's time-to-that-resource.
        # Also add mild repulsion from opponent to avoid being blocked around resources.
        score = 0
        opp_pen = dist((nx, ny), (ox, oy))
        score -= 0.10 * opp_pen
        # Choose the resource that maximizes "lead" after this move.
        local_best = -10**18
        for r in res:
            sd = dist((nx, ny), r)
            od = dist((ox, oy), r)
            if sd == 0:
                gain = 1000
            else:
                gain = (od - sd) - 0.15 * sd
            if gain > local_best:
                local_best = gain
        score += local_best
        # Deterministic tie-break: prefer smaller movement magnitude, then lexicographic (dx,dy)
        mag = abs(dx) + abs(dy)
        score -= 0.01 * mag
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score and best_move is not None:
            if (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]