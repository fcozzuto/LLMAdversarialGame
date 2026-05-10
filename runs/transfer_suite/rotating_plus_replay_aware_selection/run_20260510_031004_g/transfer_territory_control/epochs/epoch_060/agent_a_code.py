def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = observation.get("unclaimed_cells", []) or []
    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def d2(a, b, c, e): return (a - c) * (a - c) + (b - e) * (b - e)

    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves.sort(key=lambda m: (m[0], m[1]))

    if not unclaimed:
        # if nothing unclaimed, expand towards opponent boundary
        frontier = []
        for (x, y) in opp_terr:
            for dx, dy in moves[1:]:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in self_terr:
                    frontier.append((nx, ny))
        targets = frontier if frontier else list(opp_terr)
        if not targets:
            return [0, 0]
        tx, ty = min(targets, key=lambda p: (d2(sx, sy, p[0], p[1]) - 0.35 * d2(ox, oy, p[0], p[1]), d2(ox, oy, p[0], p[1]), p[0], p[1]))
    else:
        # claim unclaimed cells while preferring those closer than opponent
        tx, ty = min(unclaimed, key=lambda p: (
            (d2(sx, sy, p[0], p[1]) - 0.55 * d2(ox, oy, p[0], p[1])) + (0.02 * (abs(p[0] - (w // 2)) + abs(p[1] - (h // 2)))),
            d2(ox, oy, p[0], p[1]),
            p[0], p[1]
        ))

    # greedy step towards target, with deterministic scoring among valid moves
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # prefer reducing distance to target, and prefer entering unclaimed/opponent-claimed
        base = -(d2(nx, ny, tx, ty))
        bonus = 0
        if (nx, ny) in unclaimed:
            bonus += 180
        if (nx, ny) in opp_terr and (nx, ny) not in self_terr:
            bonus += 90
        if (nx, ny) in self_terr:
            bonus -= 5
        # also avoid stepping into tight traps behind obstacles by discouraging "dead-end" immediate backtracks
        dead = 0
        for ddx, ddy in moves[1:]:
            ax, ay = nx + ddx, ny + ddy
            if free(ax, ay):
                dead = 0
                break
        # dead-end penalty heuristic: if only return path is free
        cnt = 0
        for ddx, ddy in moves[1:]:
            ax, ay = nx + ddx, ny + ddy
            if free(ax, ay):
                cnt += 1
        if cnt <= 1:
            bonus -= 25
        score = base + bonus
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move