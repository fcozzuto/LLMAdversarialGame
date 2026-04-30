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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_margin = -10**9
        best_r = resources[0]
        for rx, ry in resources:
            our_d = cheb(sx, sy, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - our_d
            if margin > best_margin or (margin == best_margin and our_d < cheb(sx, sy, best_r[0], best_r[1])):
                best_margin = margin
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    def score_move(nx, ny):
        # Prefer grabbing a resource first; otherwise pull toward target while keeping distance from opponent.
        if resources:
            best = -10**9
            for rx, ry in resources:
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                margin = opp_d - our_d
                # Strongly favor being strictly closer than opponent, then being close overall.
                val = margin * 10 - our_d
                if (rx, ry) == (tx, ty):
                    val += 2
                if val > best:
                    best = val
            return best
        # No resources: maximize opponent distance, move toward center/target
        return cheb(nx, ny, ox, oy) * 2 - cheb(nx, ny, tx, ty)

    best_sc = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = score_move(nx, ny)
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying if equal.
        if sc > best_sc or (sc == best_sc and (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1])):
            best_sc = sc
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]