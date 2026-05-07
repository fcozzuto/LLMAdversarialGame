def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Two-phase heuristic:
        # 1) If any resource is reachable sooner by us, maximize the smallest "we-ahead" margin.
        # 2) Otherwise, minimize our distance while mildly penalizing giving the opponent advantage.
        min_opp_ahead = 10**9
        min_self_dist = 10**9
        max_we_ahead_margin = -10**9
        any_we_ahead = False
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd  # positive => we closer (so we want large)
            if sd < min_self_dist:
                min_self_dist = sd
            if margin > 0:
                any_we_ahead = True
                if margin > max_we_ahead_margin:
                    max_we_ahead_margin = margin
            else:
                if margin < min_opp_ahead:
                    min_opp_ahead = margin

        if any_we_ahead:
            # Prefer stronger immediate lead; slight tie-break for being closer.
            val = (1, max_we_ahead_margin, -min_self_dist, -(abs(nx - ox) + abs(ny - oy)))
        else:
            # Everyone is no better than we are: choose closest, but avoid helping opponent too much.
            # Here margins are <=0, so we prefer larger margin (closer to 0) plus small self distance.
            val = (0, min_opp_ahead, -min_self_dist, -(abs(nx - ox) + abs(ny - oy)))

        if best is None or val > best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]