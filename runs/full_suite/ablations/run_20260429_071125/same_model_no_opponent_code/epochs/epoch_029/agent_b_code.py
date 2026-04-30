def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if (sx, sy) in resources:
        return [0, 0]

    if resources:
        best = None
        best_adv = -10**9
        best_d1 = 10**9
        for tx, ty in resources:
            d1 = cheb(sx, sy, tx, ty)
            d2 = cheb(ox, oy, tx, ty)
            adv = d2 - d1
            if adv > best_adv or (adv == best_adv and d1 < best_d1):
                best_adv, best_d1, best = adv, d1, (tx, ty)
        target = best
    else:
        # No resources visible: move to reduce opponent influence by approaching center line.
        target = (w // 2, h // 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        valid = [(0, 0, sx, sy)]

    tx, ty = target
    best_move = None
    best_val = 10**18
    for dx, dy, nx, ny in valid:
        d_to_t = cheb(nx, ny, tx, ty)
        # Secondary: prefer moves that keep distance from opponent to avoid being intercepted.
        d_opp = cheb(nx, ny, ox, oy)
        # Deterministic tie-breaker: prefer smaller (dx,dy) lexicographically.
        val = (d_to_t * 1000) - d_opp
        if best_move is None or val < best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]