def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def toset(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obst = toset(observation.get("obstacles"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))

    opp_pos = observation.get("opponent_position") or None
    ox = oy = None
    if isinstance(opp_pos, (list, tuple)) and len(opp_pos) >= 2:
        ox, oy = int(opp_pos[0]), int(opp_pos[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_gain(x, y):
        if (x, y) in obst:
            return -10**9
        if (x, y) in oppT:
            return 7
        if (x, y) in unclaimed:
            return 4
        if (x, y) in selfT:
            return 1
        return 2

    # Targets: prefer unclaimed; if none, prefer opponent territory to counterclaim.
    if unclaimed:
        target_list = list(unclaimed)
    elif oppT:
        target_list = list(oppT)
    else:
        target_list = []
    if resources:
        # If resources exist, steer to nearest resource, but still evaluate territory flips.
        res_target = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        res_target = None

    # Deterministic tie-breaking: fixed move order.
    best = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            # Engine may keep in place; still allow [0,0] as result, but penalize invalid deltas heavily.
            continue

        score = 0
        score += cell_gain(nx, ny) * 100

        # Proximity shaping
        if res_target is not None:
            dres = abs(nx - res_target[0]) + abs(ny - res_target[1])
            score += (40 - dres)
        elif target_list:
            tx, ty = min(target_list, key=lambda p: (abs(p[0] - nx) + abs(p[1] - ny), abs(p[0] - sx) + abs(p[1] - sy)))
            d = abs(tx - nx) + abs(ty - ny)
            score += (30 - d)

        # Boundary pressure: moving near opponent increases flip potential
        if ox is not None and oy is not None:
            dop = abs(nx - ox) + abs(ny - oy)
            score += (20 - dop) if (nx, ny) in oppT else (8 - dop // 2)

        # Avoid getting stuck: prefer moves that are not isolated from our territory by obstacles when possible
        neigh_self = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if inside(ax, ay) and (ax, ay) in selfT:
                neigh_self += 1
        score += neigh_self * 3

        if score > best:
            best = score
            best_move = [dx, dy]

    # If all candidate moves were invalid (rare), stay still deterministically.
    return [int(best_move[0]), int(best_move[1])]