def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def step_greedy(px, py):
        best = None
        bd = 10**9
        for rx, ry in resources:
            d = abs(px - rx) + abs(py - ry)
            if d < bd:
                bd = d
                best = (rx, ry)
        tx, ty = best
        dx = 0 if tx == px else (1 if tx > px else -1)
        dy = 0 if ty == py else (1 if ty > py else -1)
        nx, ny = px + dx, py + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return nx, ny
        for ddx, ddy in moves:
            nx, ny = px + ddx, py + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return nx, ny
        return px, py

    p2x, p2y = step_greedy(ox, oy)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Advantage: how much closer we are to a resource than the opponent will be next.
        # Tie-break: prefer resource with larger (our distance reduction, relative).
        local_best = -10**18
        for rx, ry in resources:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(p2x - rx) + abs(p2y - ry)
            adv = do - ds  # bigger means we are closer
            val = adv * 10 + (-ds) + (rx + ry) * 0.001
            if val > local_best:
                local_best = val
        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]