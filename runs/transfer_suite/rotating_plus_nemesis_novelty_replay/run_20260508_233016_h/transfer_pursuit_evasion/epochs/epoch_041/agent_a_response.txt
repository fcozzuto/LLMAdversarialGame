def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("purs" in self_role) or ("evad" not in self_role and "purs" in opponent_role)
    # If role names are unclear, infer by points: pursuer aims to capture quickly, evader to survive.
    if "evad" in self_role and "purs" not in self_role:
        is_pursuer = False
    elif "purs" in self_role and "evad" not in self_role:
        is_pursuer = True

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        # Direct objective:
        # pursuer: minimize distance (capture ends game)
        # evader: maximize distance
        val = -dist if is_pursuer else dist

        # Small lookahead to avoid moving into bad local states (deterministic opponent step)
        opp_best = None
        opp_dist = None
        for odx, ody in dirs:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            d2 = cheb(nx, ny, tx, ty)
            # Opponent tries to maximize our distance if we are pursuer, else minimize distance to capture us.
            o_val = d2 if is_pursuer else -d2
            if opp_best is None or o_val > opp_best:
                opp_best = o_val
                opp_dist = d2
        if opp_dist is None:
            continue

        lookahead_val = (-opp_dist if is_pursuer else opp_dist)

        # Strong preference for immediate capture if pursuer
        if is_pursuer and opp_dist == 0:
            lookahead_val = 10**9

        if best_val is None or lookahead_val > best_val:
            best_val = lookahead_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]