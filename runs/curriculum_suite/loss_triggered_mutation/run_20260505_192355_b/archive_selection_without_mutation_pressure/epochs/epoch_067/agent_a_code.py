def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # If no visible resources, drift to center while keeping distance from opponent
    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = (man(nx, ny, cx, cy), -man(nx, ny, ox, oy), dx, dy)
            if best is None or v < bestv:
                bestv, best = v, (dx, dy)
        return list(best) if best is not None else [0, 0]

    # One-step advantage: for the best resource for us, maximize (opp_min - self_min),
    # plus a small tie-break to avoid giving the opponent the same immediate target.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Best target for us from (nx,ny)
        self_min = 10**9
        opp_at_that = 10**9
        self_target = None
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            if d_self < self_min:
                self_min = d_self
                opp_at_that = man(ox, oy, rx, ry)
                self_target = (rx, ry)
            elif d_self == self_min and man(ox, oy, rx, ry) < opp_at_that:
                opp_at_that = man(ox, oy, rx, ry)
                self_target = (rx, ry)

        # Opponent's closest resource overall (baseline pressure)
        opp_min = 10**9
        for rx, ry in resources:
            d_opp = man(ox, oy, rx, ry)
            if d_opp < opp_min:
                opp_min = d_opp

        # Encourage moves that keep opponent far from our chosen target,
        # while also not making the opponent generally closer to resources.
        advantage = opp_min - self_min
        block = opp_at_that - self_min  # larger means we are relatively closer to our target
        # Tie-break: prefer increasing distance from opponent, then lexicographic on move
        dist_opp = man(nx, ny, ox, oy)
        score_tuple = (-(advantage), -(block), -dist_opp, dx, dy)

        if best_score is None or score_tuple < best_score:
            best_score = score_tuple
            best_move = [dx, dy]

    return best_move