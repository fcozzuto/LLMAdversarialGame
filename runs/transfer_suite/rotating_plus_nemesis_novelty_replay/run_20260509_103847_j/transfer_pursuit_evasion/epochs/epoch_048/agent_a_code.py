def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    sr = (observation.get("self_role") or "").lower()
    pr = (observation.get("opponent_role") or "").lower()
    purs = ("purs" in sr) or ("catch" in sr) or ("hunt" in sr) or ("chaser" in sr) or ("pursuer" in sr) or ("tagger" in sr)
    if (not purs) and (("purs" in pr) or ("catch" in pr) or ("hunt" in pr) or ("chaser" in pr) or ("pursuer" in pr) or ("tagger" in pr)):
        purs = False
    evad = not purs

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = []
    for dx in dxs:
        for dy in dys:
            if not (dx == 0 and dy == 0):
                moves.append((dx, dy))
    moves.append((0, 0))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
    farx, fary = far_corner

    pref = (observation.get("turn_index", 0) & 1)
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # Deterministic tie-break preference: slightly favor alternating axis.
        axis_bonus = 0
        if pref == 0:
            axis_bonus = 0.01 * (-abs(ny - sy) + abs(nx - sx))
        else:
            axis_bonus = 0.01 * (-abs(nx - sx) + abs(ny - sy))

        if purs:
            score = -dist2 + axis_bonus
        else:
            corner_dist = abs(farx - nx) + abs(fary - ny)
            score = dist2 - 0.02 * corner_dist + axis_bonus

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]