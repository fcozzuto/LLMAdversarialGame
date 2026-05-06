def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            q = r.get("position")
        else:
            q = r
        if isinstance(q, (list, tuple)) and len(q) >= 2:
            x, y = int(q[0]), int(q[1])
            if inb(x, y) and (x, y) not in blocked:
                rpos.append((x, y))

    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        my_best = 10**9
        max_adv = -10**9
        # advantage: how much closer I am than opponent to the same resource
        for rx, ry in rpos:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if my_d < my_best:
                my_best = my_d
            adv = opp_d - my_d
            if adv > max_adv:
                max_adv = adv

        # maximize denial/advantage first, then minimize my_best; deterministic tie-break by move order
        key = (-max_adv, my_best, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]