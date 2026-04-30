def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        if resources:
            d_res = 10**9
            tieb = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < d_res:
                    d_res = d
                    tieb = (rx, ry)
                elif d == d_res and (rx, ry) < tieb:
                    tieb = (rx, ry)
            tx, ty = tieb
        else:
            d_res = 0
            tx, ty = nx, ny

        # Higher is better: get closer to resources, keep some separation from opponent,
        # prefer moving in direction that reduces distance to chosen target deterministically.
        # Primary: -d_res, Secondary: +d_opp, Tertiary: tie-break by deterministic target progress.
        dir_prog = 0
        if resources:
            # If moving toward target reduces cheb, give bonus; otherwise penalty
            dir_prog = cheb(sx, sy, tx, ty) - cheb(nx, ny, tx, ty)

        score = (-d_res * 1000) + (d_opp * 10) + dir_prog
        if best is None or score > best:
            best = score
            best_move = (dx, dy)
        elif score == best:
            # Deterministic tie-break: lexicographic preference of move deltas
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]