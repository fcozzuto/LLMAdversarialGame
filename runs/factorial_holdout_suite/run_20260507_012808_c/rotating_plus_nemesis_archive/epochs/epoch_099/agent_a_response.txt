def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)
    best_target = resources[0]
    best_key = None

    for t in resources:
        dm = man(my, t)
        do = man(opp, t)
        # Prefer resources we can reach strictly earlier; if tie, prefer higher relative advantage.
        key = (0 if dm < do else 1, dm - do, dm, do, t[0], t[1])
        if best_key is None or key < best_key:
            best_key = key
            best_target = t

    tx, ty = best_target
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Also compute opponent's nearest resource to estimate threat.
    opp_best = None
    opp_best_d = 10**9
    for t in resources:
        d = man(opp, t)
        if d < opp_best_d:
            opp_best_d = d
            opp_best = t
    ot = opp_best

    # Score: reduce our distance to chosen target; if equal, increase distance between opponent and their closest.
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        nm = man((nx, ny), (tx, ty))
        no_to_opp = man(opp, (ot[0], ot[1])) if ot is not None else 0
        # If we get closer to our target, we deny less; so primary is nm. Secondary: maximize how much we can make opponent waste.
        # Approx deny effect: compare our next distance to their nearest relative to ours.
        nm_to_opp = man((nx, ny), (ot[0], ot[1])) if ot is not None else 0
        threat = nm_to_opp - no_to_opp
        score = (nm, threat, man((nx, ny), (tx, ty)) - man(opp, (tx, ty)), abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]