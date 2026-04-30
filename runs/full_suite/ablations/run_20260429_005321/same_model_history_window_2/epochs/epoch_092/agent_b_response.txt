def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w - 1, h - 1
    else:
        tx = ty = resources[0][0], resources[0][1]
        best = -10**18
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer (od-md positive), also lightly prefer far-priority to break ties.
            s = (od - md) * 10 - md - (rx + ry) * 0.01
            if s > best:
                best = s
                tx, ty = rx, ry

    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_to_t = cheb(nx, ny, tx, ty)
        op_to_t = cheb(ox, oy, tx, ty)
        # Greedy toward target, but also avoid giving opponent an advantage by not moving into their race-line when possible.
        my_slack = op_to_t - my_to_t
        op_prox = -cheb(nx, ny, ox, oy)
        v = my_slack * 10 - my_to_t + op_prox * 0.2
        # If tied, prefer moves that reduce my distance more.
        if v > bestv or (v == bestv and my_to_t < cheb(sx, sy, tx, ty)):
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]