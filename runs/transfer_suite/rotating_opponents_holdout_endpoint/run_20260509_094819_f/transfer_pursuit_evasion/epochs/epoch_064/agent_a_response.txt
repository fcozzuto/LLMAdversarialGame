def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    sr = (observation.get("self_role") or "").lower()
    self_pursuer = "pursuer" in sr

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = [0, 0]
    best_score = None

    for dx, dy in cand:
        nsx, nsy = sx + dx, sy + dy
        if not legal(nsx, nsy):
            continue

        # Opponent best response in one step (assume opponent is the other role)
        if self_pursuer:
            # opponent is evader: maximize distance after response
            opp_best = -1
            for odx, ody in cand:
                nox, noy = ox + odx, oy + ody
                if not legal(nox, noy):
                    continue
                d = dist(nsx, nsy, nox, noy)
                if d > opp_best:
                    opp_best = d
            if opp_best < 0:
                opp_best = dist(nsx, nsy, ox, oy)
            score = -opp_best  # pursuer wants smaller distance
        else:
            # opponent is pursuer: minimize distance after response
            opp_best = 10**9
            for odx, ody in cand:
                nox, noy = ox + odx, oy + ody
                if not legal(nox, noy):
                    continue
                d = dist(nsx, nsy, nox, noy)
                if d < opp_best:
                    opp_best = d
            if opp_best == 10**9:
                opp_best = dist(nsx, nsy, ox, oy)
            score = opp_best  # evader wants larger distance

        # deterministic tie-break: prefer larger score, then lexicographically smaller [dx,dy]
        if best_score is None or score > best_score or (score == best_score and [dx, dy] < best_move):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]