def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    candidates = list(unclaimed)
    if not candidates:
        candidates = resources[:] if resources else [((w - 1) // 2, (h - 1) // 2)]

    best_target = None
    best_score = None
    for tx, ty in candidates:
        if (tx, ty) in obs:
            continue
        d_self = abs(tx - sx) + abs(ty - sy)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Prefer grabbing close unclaimed, and slightly deny opponent by aiming away from their proximity
        # while also encouraging contact with our frontier.
        frontier = 0
        for (nx, ny) in ((tx + 1, ty), (tx - 1, ty), (tx, ty + 1), (tx, ty - 1), (tx + 1, ty + 1), (tx - 1, ty - 1), (tx + 1, ty - 1), (tx - 1, ty + 1)):
            if (nx, ny) in self_t:
                frontier = 1
                break
        sc = d_self - 0.12 * d_opp - 1.8 * frontier
        if best_score is None or sc < best_score or (sc == best_score and (ty, tx) < (best_target[1], best_target[0])):
            best_score = sc
            best_target = (tx, ty)

    tx, ty = best_target if best_target is not None else ((w - 1) // 2, (h - 1) // 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_dist = None
    best_tie = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        # If equal distance, prefer moves that move closer to opponent territory (helps flip on contact)
        tie = abs(nx - ox) + abs(ny - oy) - (1 if (nx, ny) in opp_t else 0)
        if best_dist is None or dist < best_dist or (dist == best_dist and (tie, ny, nx) < best_tie):
            best_dist = dist
            best_tie = (tie, ny, nx)
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]