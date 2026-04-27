def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_val = -10**18
    moves_considered = 0

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            moves_considered += 1
            v = -cheb(nx, ny, ox, oy)  # deterministic fallback: approach opponent
            if v > best_val or (v == best_val and (dx, dy) < best_move):
                best_val = v
                best_move = (dx, dy)
        if moves_considered == 0:
            return [0, 0]
        return [best_move[0], best_move[1]]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        moves_considered += 1
        d_op_next = cheb(nx, ny, ox, oy)
        block = 0
        if d_op_next <= 1:
            block = 200  # avoid getting too close
        # Choose best resource for this move
        v_best = -10**18
        for rx, ry in resources:
            d_s = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            # advantage if we reach sooner than opponent
            v = (d_o - d_s) * 60 - d_s * 3
            # slight bias toward closer resources when similar advantage
            if v > v_best:
                v_best = v
        v_total = v_best - block
        if v_total > best_val or (v_total == best_val and (dx, dy) < best_move):
            best_val = v_total
            best_move = (dx, dy)

    if moves_considered == 0:
        return [0, 0]
    return [best_move[0], best_move[1]]