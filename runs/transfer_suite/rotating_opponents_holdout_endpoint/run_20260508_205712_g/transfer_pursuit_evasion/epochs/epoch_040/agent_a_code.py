def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in role) or (("pursuer" in opp_role) and ("evader" not in role))
    if ("evader" in role) and ("pursuer" not in role):
        pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best1(nx, ny, targetx, targety, sign):
        # sign=+1 prefers closer; sign=-1 prefers farther
        best = None
        for dx, dy in moves:
            x2, y2 = nx + dx, ny + dy
            if not free(x2, y2):
                continue
            d1 = cheb(x2, y2, targetx, targety)
            # local "escape room" to avoid dead-ends
            room = 0
            for ddx, ddy in moves:
                xx, yy = x2 + ddx, y2 + ddy
                if free(xx, yy):
                    room += 1
            score = sign * d1 + (0.03 * room)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return best[1:] if best is not None else (0, 0)

    best_move = (0, 0)
    best_score = None
    sign = +1 if pursuer else -1  # pursuer: minimize distance; evader: maximize distance
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # 2-step lookahead: our move then assume opponent does best for their objective
        if pursuer:
            # after we move, opponent is evader -> likely increases distance
            adx, ady = best1(nx, ny, ox, oy, sign=-1)
        else:
            # after we move, opponent is pursuer -> likely decreases distance
            adx, ady = best1(nx, ny, ox, oy, sign=+1)
        px, py = nx + adx, ny + ady
        d_after = cheb(px, py, ox, oy) if pursuer else cheb(px, py, ox, oy)
        # convert to our preference (pursuer wants small, evader wants large)
        pref = d_after if pursuer else -d_after
        room = 0
        for ddx, ddy in moves:
            xx, yy = nx + ddx, ny + ddy
            if free(xx, yy):
                room += 1
        score = pref + (-0.02 * room if pursuer else 0.02 * room)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]