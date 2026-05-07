def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_res = None
    best_val = (-10**18, 10**18, 10**18)
    for rx, ry in resources:
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        # Prefer resources where we are closer than opponent; tie-break by smaller own distance.
        # Secondary tie-break: prefer lower (rx+ry) to stay deterministic.
        val = (od - sd, -sd, -(rx + ry))
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res
    # If an adjacent move can directly collect a resource, take the best among them.
    adj_best = None
    adj_val = (-10**18, 10**18, 10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in set(resources):
            sd2 = 0
            od2 = man((ox, oy), (nx, ny))
            val2 = (od2 - sd2, -sd2, -(nx + ny))
            if val2 > adj_val:
                adj_val = val2
                adj_best = (dx, dy)

    if adj_best is not None:
        return [int(adj_best[0]), int(adj_best[1])]

    # Otherwise, step toward target with a defensive twist: reduce opponent's relative advantage.
    best_move = (0, 0)
    best_move_val = (-10**18, 10**18, 10**18)
    target_res = (tx, ty)
    nxset = set(resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd = man((nx, ny), target_res)
        od = man((ox, oy), target_res)
        # If opponent is closer, try to improve relative gap by staying on paths that keep (od - sd) large.
        rel = od - sd
        val = (rel, -sd, -(nx + ny))
        # Small bonus if the move also brings us adjacent to any resource (material progress).
        for rx, ry in resources:
            if man((nx, ny), (rx, ry)) == 0:
                break
        if (nx, ny) in nxset:
            val = (val[0] + 10**6, val[1], val[2])
        if val > best_move_val:
            best_move_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]