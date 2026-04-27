def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w - 1, h - 1  # default to opposite corner
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # also drift away from opponent a bit
            da = cheb(nx, ny, ox, oy)
            sc = -d + 0.1 * da
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    best = None
    opp_to = [(r, cheb(ox, oy, r[0], r[1])) for r in resources]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_best = None
        my_closest = 10**9
        for r, od in opp_to:
            d = cheb(nx, ny, r[0], r[1])
            my_closest = d if d < my_closest else my_closest
            # score resources where I'm closer than opponent
            rel = od - d  # positive if I can beat opponent to it
            cand = 0.0
            cand += 6.0 * rel
            cand += -0.9 * d
            if d == 0:
                cand += 100.0
            if my_best is None or cand > my_best:
                my_best = cand
        # prefer moves that reduce my closest distance; and keep some separation
        sep = cheb(nx, ny, ox, oy)
        sc = (my_best if my_best is not None else -my_closest) - 0.4 * my_closest + 0.05 * sep
        if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)

    return [best[1], best[2]] if best is not None else [0, 0]