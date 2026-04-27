def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target selection: pick a resource that we can reach no later than opponent, and otherwise the "next best"
    if resources:
        best = None
        for rx, ry in resources:
            dm = man((mx, my), (rx, ry))
            do = man((ox, oy), (rx, ry))
            # Prefer resources we can secure; break ties deterministically by coordinates
            key = (do - dm, dm, rx, ry)  # maximize (do-dm) => smallest key first since we use ascending
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources: head to midline away from opponent to reduce overlap
        tx, ty = (w // 2 if mx < w // 2 else (w // 2 - 1), h // 2)

    # Predict opponent's greedy next move toward target
    def opp_next():
        bestm = (0, 0)
        bestk = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny):
                continue
            k = (man((nx, ny), (tx, ty)), nx, ny)
            if bestk is None or k < bestk:
                bestk = k
                bestm = (dx, dy)
        return bestm

    odx, ody = opp_next()
    pox, poy = ox + odx, oy + ody

    # Evaluate candidate moves
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not inb(nx, ny):
            continue

        # Base: get closer to target
        d_my = man((nx, ny), (tx, ty))

        # Pressure: increase distance from opponent's next position
        d_op = man((nx, ny), (pox, poy))

        # Block: prefer stepping into cells that are on opponent's greedy path directionally
        # (simple proxy: minimize opponent distance if it moves there)
        opp_if_take = man((pox, poy), (tx, ty))

        # Safety: avoid being adjacent/overlapping to reduce mutual blocking
        adjacent_pen = 0
        if man((nx, ny), (ox, oy)) <= 1:
            adjacent_pen = 3

        val = (-d_my, d_op, -opp_if_take, adjacent_pen, nx, ny, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]