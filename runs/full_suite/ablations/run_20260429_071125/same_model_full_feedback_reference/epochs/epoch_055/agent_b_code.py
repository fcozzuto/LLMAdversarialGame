def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            key = (d, rx, ry)
            if best is None or key < best:
                best = key
                target = (rx, ry)

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if target is None:
            # No resources visible: drift away from opponent while biasing toward center
            dist_op = cheb(nx, ny, ox, oy)
            center = cheb(nx, ny, w // 2, h // 2)
            score = (-dist_op, center, 0, dx, dy)
        else:
            rx, ry = target
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(nx, ny, ox, oy)  # used to avoid immediate contest
            # If opponent can reach target quicker, prioritize escape/positioning
            op_reach = cheb(ox, oy, rx, ry)
            opp_bias = 1 if my_d >= op_reach else 0
            score = (my_d, opp_bias, op_d, abs(nx - rx) + abs(ny - ry), dx, dy)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]