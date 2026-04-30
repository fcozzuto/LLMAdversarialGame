def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, drift toward opponent's side to contest future spawns.
    if not resources:
        tx, ty = (w - 1, 0) if (sx + sy) <= (ox + oy) else (0, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs_order = sorted(moves, key=lambda d: (d[0], d[1]))

    # Choose globally best resource, then pick the move that maximizes post-move advantage.
    best_target = None
    best_base = None
    for r in resources:
        myd = cheb((sx, sy), r)
        opd = cheb((ox, oy), r)
        # Base: stealing potential then closeness.
        base = (opd - myd, -myd, -r[0], -r[1])
        if best_base is None or base > best_base:
            best_base = base
            best_target = r

    tx, ty = best_target
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs_order:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        myd = cheb((nx, ny), (tx, ty))
        opd = cheb((ox, oy), (tx, ty))
        # Extra shaping: keep moving generally toward target; also block if we can get closer than opponent.
        toward = -(abs(tx - nx) + abs(ty - ny))
        score = (opd - myd, -myd, toward)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    # If all moves were invalid (should be rare), try a safe default.
    if best_score is None:
        for dx, dy in dirs_order:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]