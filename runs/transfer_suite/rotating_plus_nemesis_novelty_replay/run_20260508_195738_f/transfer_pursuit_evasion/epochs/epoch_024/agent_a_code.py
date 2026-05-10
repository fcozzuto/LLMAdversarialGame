def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))
    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))
    resources = observation.get("resources", []) or []
    opp = (int(ox), int(oy))
    selfp = (int(sx), int(sy))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    # Role inference: treat "evader" keyword as avoid-opponent, else pursue.
    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    evader = ("evader" in roles) and ("purs" not in roles)

    best = None
    bestmove = (0, 0)

    if resources:
        # Choose nearest resource; tie-break deterministically by coordinates.
        tx, ty = resources[0]
        tx, ty = int(tx), int(ty)
        bd = 10**18
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                d = abs(rx - selfp[0]) + abs(ry - selfp[1])
                if d < bd or (d == bd and (rx, ry) < (tx, ty)):
                    bd = d
                    tx, ty = rx, ry
    else:
        tx, ty = opp if not evader else (0, 0)

    for dx, dy in deltas:
        nx, ny = selfp[0] + dx, selfp[1] + dy
        if not ok(nx, ny):
            continue
        # Score: pursue resources, and either move toward or away from opponent depending on role.
        dr = abs(tx - nx) + abs(ty - ny)
        do = abs(opp[0] - nx) + abs(opp[1] - ny)
        s = 0
        if resources:
            s += -dr
        # If no resources, still try to gain by opponent relation.
        s += (do if evader else -do)
        # Deterministic tie-break by move.
        if best is None or s > best or (s == best and (dx, dy) < bestmove):
            best = s
            bestmove = (dx, dy)

    # If all moves blocked, stay.
    return [int(bestmove[0]), int(bestmove[1])]