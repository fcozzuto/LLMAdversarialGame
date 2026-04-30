def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    # If no visible resources, drift toward center while keeping away from obstacles/opponent
    if not resources:
        tx = w // 2
        ty = h // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            v = cheb(nx, ny, tx, ty) + 0.2 * cheb(nx, ny, ox, oy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Main: choose move that maximizes "secure" advantage over opponent for best contested resource
    # Advantage is (op_dist - my_dist): larger means I can reach sooner.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_best = 10**9
        opp_best = 10**9
        adv_best = -10**9
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Penalize resources where opponent is already much closer
            adv = od - md
            if adv > adv_best:
                adv_best = adv
                my_best = md
                opp_best = od

        # Reward reaching soon and winning contests; lightly penalize being near opponent after move
        score = (adv_best * 100.0) - (my_best * 2.0) + ((my_best <= opp_best) * 10.0) - 0.1 * cheb(nx, ny, ox, oy)

        # Deterministic tie-breaker: prefer moves with smaller dx then dy magnitude and then staying
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            cand = (abs(dx), abs(dy), 0 if (dx == 0 and dy == 0) else 1)
            bestcand = (abs(best_move[0]), abs(best_move[1]), 0 if (best_move[0] == 0 and best_move[1] == 0) else 1)
            if cand < bestcand:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]