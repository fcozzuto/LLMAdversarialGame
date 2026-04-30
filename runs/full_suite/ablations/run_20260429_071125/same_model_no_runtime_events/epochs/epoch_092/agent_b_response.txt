def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if legal(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best = ( -10**18, (0, 0) )
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -(cheb(nx, ny, ox, oy))  # drift away from opponent
            if v > best[0]:
                best = (v, (dx, dy))
        return [best[1][0], best[1][1]]

    cur_best_target_dist = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < cur_best_target_dist:
            cur_best_target_dist = d

    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = 0.0
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer immediate/near resources strongly; then prefer resources we beat the opponent on.
            val += 100.0 / (1 + d_me)
            if d_me < d_op:
                val += 50.0 / (1 + d_me)
            else:
                # If opponent is closer or equal, slightly discourage contesting unless very near.
                if d_me <= cur_best_target_dist:
                    val -= 20.0 / (1 + d_me)
        # Mildly prefer moves that reduce our distance to the currently best target
        val += 2.0 * (cur_best_target_dist - cheb(nx, ny, resources[0][0], resources[0][1]))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]