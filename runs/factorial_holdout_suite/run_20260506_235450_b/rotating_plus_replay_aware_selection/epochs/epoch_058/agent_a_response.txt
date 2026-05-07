def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    legal = []
    for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    # Pick best target by who is closer in Chebyshev distance (turns), then by urgency.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        cand = (do - ds, -max(ds, 0), -ds, rx, ry)
        if best is None or cand > best[0]:
            best = (cand, rx, ry)
    _, tx, ty = best

    # Try to move greedily toward chosen target but keep obstacle-legal.
    step_dx = 0 if tx == sx else (1 if tx > sx else -1)
    step_dy = 0 if ty == sy else (1 if ty > sy else -1)
    preferred = (step_dx, step_dy, sx + step_dx, sy + step_dy)
    for dx, dy, nx, ny in legal:
        if (dx, dy, nx, ny) == preferred:
            return [dx, dy]

    # Otherwise, evaluate legal moves by resulting advantage to the best targets.
    # Deterministic: break ties by preferring smaller self distance.
    def cell_adv(nx, ny):
        best_adv = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds2 = cheb(nx, ny, rx, ry)
            do2 = cheb(ox, oy, rx, ry)
            cand = (do2 - ds2, -ds2, rx, ry)
            if best_adv is None or cand > best_adv:
                best_adv = cand
        return best_adv

    best_move = None
    for dx, dy, nx, ny in legal:
        adv = cell_adv(nx, ny)
        cand = (adv[0], adv[1], -cheb(nx, ny, tx, ty), dx, dy)
        if best_move is None or cand > best_move[0]:
            best_move = (cand, dx, dy)
    return [int(best_move[1]), int(best_move[2])]