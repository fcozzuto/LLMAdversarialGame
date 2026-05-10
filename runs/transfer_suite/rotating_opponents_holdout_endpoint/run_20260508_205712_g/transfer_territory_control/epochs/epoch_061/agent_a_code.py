def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    unclaimed = observation.get("unclaimed_cells") or []
    my_terr = observation.get("self_territory") or []
    their_terr = observation.get("opponent_territory") or []
    obs_list = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obs_list:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    my_terr_set = set((int(x), int(y)) for x, y in my_terr)
    their_terr_set = set((int(x), int(y)) for x, y in their_terr)
    unclaimed_set = set((int(x), int(y)) for x, y in unclaimed)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    adj_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    opp_adj = set()
    for x, y in their_terr_set:
        for dx, dy in adj_dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed_set:
                opp_adj.add((nx, ny))

    border_targets = [(x, y) for (x, y) in unclaimed_set if x in (0, w - 1) or y in (0, h - 1)]
    if opp_adj:
        targets = list(opp_adj)
    elif border_targets:
        targets = border_targets
    else:
        targets = list(unclaimed_set) or list(unclaimed) or [(sx, sy)]

    if not targets:
        return [0, 0]

    # Deterministic target choice: closest; tie-break by lexicographic (x,y)
    best_t = None
    best_d = None
    for x, y in targets:
        if not inb(x, y):
            continue
        d = (abs(x - sx) + abs(y - sy))
        if best_d is None or d < best_d or (d == best_d and (x, y) < best_t):
            best_d = d
            best_t = (x, y)
    tx, ty = best_t

    # Choose move that best approaches target and (secondarily) expands territory front
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = abs(tx - nx) + abs(ty - ny)

        # Bonus for moving into cells adjacent to opponent territory (likely flip/contend)
        front = 0
        for adx, ady in adj_dirs:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in their_terr_set:
                front = 1
                break

        # Slight preference to avoid getting stuck in already-owned area if target is far
        in_my = 1 if (nx, ny) in my_terr_set else 0
        score = (dist, -front, in_my, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]