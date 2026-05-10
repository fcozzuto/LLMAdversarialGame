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

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in self_role) or ("tag" in self_role) or ("hunter" in self_role)
    if not pursuer:
        pursuer = ("purs" in opp_role) or ("tag" in opp_role) or ("hunter" in opp_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    best_move = [0, 0]
    bestv = None
    for dx, dy in dirs:
        nsx, nsy = sx + dx, sy + dy
        if not valid(nsx, nsy):
            continue

        # Opponent one-ply response: assume opponent chooses moves that help their objective.
        vals = []
        for odx, ody in dirs:
            nox, noy = ox + odx, oy + ody
            if not valid(nox, noy):
                continue
            dist2 = (nsx - nox) * (nsx - nox) + (nsy - noy) * (nsy - noy)
            vals.append(dist2)
        if not vals:
            vals = [(nsx - ox) * (nsx - ox) + (nsy - oy) * (nsy - oy)]

        if pursuer:
            # We want to get caught quickly: maximize negative of opponent's best (largest) distance.
            v = -max(vals)
        else:
            # We want to evade: maximize opponent's worst (smallest) distance.
            v = min(vals)

        if bestv is None or v > bestv or (v == bestv and (dx, dy) < (best_move[0], best_move[1])):
            bestv = v
            best_move = [dx, dy]

    return best_move