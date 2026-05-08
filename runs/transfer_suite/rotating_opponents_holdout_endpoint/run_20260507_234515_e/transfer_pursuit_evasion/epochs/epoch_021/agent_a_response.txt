def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in srole) or ("catch" in srole) or ("seeker" in srole) or ("chase" in srole)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18 if is_pursuer else 10**18
    curd = cheb(sx, sy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        d = cheb(nx, ny)
        center = -((abs(nx - cx) + abs(ny - cy)))
        # Prefer diagonal-ish progress: smaller dx-dy alignment penalty for pursuer, opposite for evader
        align = -(abs((nx - ox) - (ny - oy)))
        if is_pursuer:
            # Primary: minimize distance. Strongly prefer capture (d==0).
            score = -1000 * d
            # Keep moving toward opponent (avoid increasing distance)
            score += 50 * (curd - d)
            score += 5 * center + 2 * align
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            # Evader: maximize distance; avoid corners only if it helps distance (handled by corner targets implicitly)
            score = 1000 * d
            score += 50 * (d - curd)
            score += -5 * center + -2 * align  # drift toward edges/corners; align pushes away from pursuer direction
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]