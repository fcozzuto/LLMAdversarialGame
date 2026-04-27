def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        resources = [(ox, oy)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = [0, 0]
    best_val = -10**9

    # Heuristic weights: aim for resources; if opponent is very close, bias towards blocking (reduce distance to opponent too).
    res_bias = 10
    opp_bias = 2 if cheb(sx, sy, ox, oy) <= 2 else 1

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue

            dmin = 10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d = cheb(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d

            # Higher is better: closer to resource increases value; also slight preference to approach opponent when close.
            val = (-res_bias * dmin) - (opp_bias * cheb(nx, ny, ox, oy))
            # Deterministic tie-break: prefer smaller dx, then smaller dy by using lexicographic value adjustment.
            val += -(abs(dx) * 0.01 + abs(dy) * 0.001)

            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move