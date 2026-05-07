def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    if (sx, sy) in obst or not res:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If already on resource, stay still to guarantee collection.
    if (sx, sy) in res:
        return [0, 0]

    # Score a neighbor by best target advantage reachable from that neighbor.
    # Encourage creating separation: we prefer targets where we are earlier than opponent,
    # otherwise we pick the one that minimizes opponent's lead.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        my_pos = (nx, ny)
        local_best = -10**18
        for tx, ty in res:
            t = (tx, ty)
            sd = d(my_pos, t)
            od = d((ox, oy), t)
            lead = od - sd  # positive if we reach earlier
            # Prefer immediate collection strongly; also break ties by smaller self distance.
            val = lead * 1000 - sd
            if lead >= 0:
                val += 10000
            # If opponent is already on target, reduce urgency for that cell.
            if (ox, oy) == t:
                val -= 100000
            if val > local_best:
                local_best = val

        # Secondary tie-break: prefer moves that reduce distance to the "most contested" cells
        # (ones where opponent is currently close).
        contested = 0
        for tx, ty in res:
            od = d((ox, oy), (tx, ty))
            if od <= 2:
                contested += 1
        if local_best > best_val or (local_best == best_val and (nx + ny) < (best_move[0] + best_move[1])):
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]