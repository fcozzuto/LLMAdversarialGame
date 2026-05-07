def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_for(posx, posy, oppx, oppy):
        best = None
        best_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = cheb(posx, posy, rx, ry)
            od = cheb(oppx, oppy, rx, ry)
            key = (1 if sd < od else 0, od - sd, -sd, -(rx + 3 * ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry, sd, od)
        return best

    opp_target = best_for(ox, oy, sx, sy)
    tx0, ty0 = (opp_target[0], opp_target[1]) if opp_target else (sx, sy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        best_adv = -10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we can arrive first; also prefer smaller distances once parity is broken.
            adv = (10 if myd < opd else 0) + (opd - myd) * 2 - myd * 0.15
            if adv > best_adv:
                best_adv = adv

        # Denial pressure: reduce distance to opponent's best resource.
        myd_t = cheb(nx, ny, tx0, ty0)
        od_t = cheb(ox, oy, tx0, ty0)
        deny = (10 if myd_t < od_t else 0) + (od_t - myd_t) - myd_t * 0.05

        score = best_adv + deny
        tie = (deny, best_adv, -cheb(nx, ny, tx0, ty0), -(nx + 7 * ny))
        if best_score is None or score > best_score or (score == best_score and tie > best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]