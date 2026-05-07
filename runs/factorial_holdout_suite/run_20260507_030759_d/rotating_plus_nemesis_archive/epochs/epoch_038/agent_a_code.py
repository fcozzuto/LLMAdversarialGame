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

    if (sx, sy) in res:
        return [0, 0]
    if not res:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        my_pos = (nx, ny)
        # Choose the resource that maximizes our advantage from this next position.
        # Advantage favors: (we are closer than opponent) and (we're closer overall).
        best_adv = -10**18
        for r in res:
            my_d = man(my_pos, r)
            op_d = man((ox, oy), r)
            # Large weight on being closer; secondary on speed; slight bias away from contested far traps.
            adv = (op_d - my_d) * 100 - my_d
            if adv > best_adv:
                best_adv = adv

        # If we are not improving advantage, still prefer moves that reduce our distance to the best resource.
        if best_adv > bestv or (best_adv == bestv and (nx, ny) < best):
            bestv = best_adv
            best = (dx, dy)

    return [int(best[0]), int(best[1])]