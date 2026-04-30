def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    # Choose target: prioritize resources I can reach earlier; penalize those opponent can beat me to.
    best_t = None
    best_k = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # If standing on/adjacent, take it; also slight tie-break to avoid giving opponent free choice.
        k = (0 if myd == 0 else 1, myd, -(opd - myd), rx + ry)
        # If I'm strictly closer, strongly prefer; if equal, prefer where opponent is farther.
        if myd == 0:
            k = (-1, 0, -(opd), rx + ry)
        else:
            k = (0 if myd < opd else 1, myd, -(opd), rx + ry)
        if best_k is None or k < best_k:
            best_k = k
            best_t = (rx, ry)

    tx, ty = best_t
    # Step greedily toward target with obstacle avoidance; tie-break by reducing opponent distance slightly.
    best_move = (0, 0)
    best_mk = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        # If move lands on a resource, prefer it strongly.
        on_res = 1 if (nx, ny) in resources else 0
        d_opp = cheb(nx, ny, ox, oy)
        mk = (-on_res, d_to, d_opp, dx, dy)
        if best_mk is None or mk < best_mk:
            best_mk = mk
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]