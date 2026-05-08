def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    opp_turn_pref = 1 if (observation.get("turn_index", 0) or 0) % 2 == 0 else -1

    best = None
    tx, ty = resources[0]
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer winning race; tie-break by closer resource and lower coordinate.
        score = ((do - ds) * 100 + (1 if ds == 0 else 0), -(ds + cheb(rx, ry, w-1, h-1) * 0.01),
                 -(rx * 31 + ry))
        if best is None or score > best:
            best = score
            tx, ty = rx, ry

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Deterministic order, already fixed.

    bestm = [0, 0]
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        # Estimate opponent distance if they move 1 step toward the same target.
        ox_best = ox
        oy_best = oy
        step_dx = 0 if tx == ox else (1 if tx > ox else -1)
        step_dy = 0 if ty == oy else (1 if ty > oy else -1)
        ox_best, oy_best = ox + step_dx, oy + step_dy
        if not inb(ox_best, oy_best) or (ox_best, oy_best) in obstacles:
            ox_best, oy_best = ox, oy
        no = cheb(ox_best, oy_best, tx, ty)

        v = ((no - ns) * 100 + (1 if (nx, ny) == (tx, ty) else 0),
             -ns, -((nx * 31 + ny) + opp_turn_pref * 0))
        if bestv is None or v > bestv:
            bestv = v
            bestm = [dx, dy]

    return bestm