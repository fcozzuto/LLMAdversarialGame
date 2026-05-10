def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    srole = str(observation.get("self_role", "")).lower()
    self_pursuer = ("purs" in srole) or ("chaser" in srole) or ("hunter" in srole) or ("pursuer" in srole)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def avoid_score(x, y):
        # Penalize being adjacent to obstacles (simple local wall-avoidance)
        pen = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                pen += 1
        return pen

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_bias(x, y):
        # Prefer moving toward the farthest corner relative to opponent (evader behavior)
        bx = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        return - (abs(x - bx[0]) + abs(y - bx[1]))

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # capture check (radius 0): if moving onto opponent, pursuer wins immediately; evader avoids if possible
        if nx == ox and ny == oy:
            metric = (-10**9 if self_pursuer else 10**9)
        else:
            d = cheb(nx, ny, ox, oy)
            wall = avoid_score(nx, ny)
            if self_pursuer:
                # chase: minimize distance, also prefer lower wall penalty; discourage stepping "around" obstacles by biasing to closer corners
                metric = d * 10 - wall * 3 + corner_bias(nx, ny)
                # smaller is better
                metric = metric
            else:
                # evade: maximize distance; avoid obstacles; also head toward farthest corner
                metric = -d * 10 - wall * 3 + corner_bias(nx, ny)
                # larger is better, so negate-distance + biases above already arranged

        # Make selection consistent; deterministic tie-break by move ordering already fixed
        if best is None:
            best, best_move = metric, [dx, dy]
        else:
            if self_pursuer:
                if metric < best:
                    best, best_move = metric, [dx, dy]
            else:
                if metric > best:
                    best, best_move = metric, [dx, dy]

    return [int(best_move[0]), int(best_move[1])]