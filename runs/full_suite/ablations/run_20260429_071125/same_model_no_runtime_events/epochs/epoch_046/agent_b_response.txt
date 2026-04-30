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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_best = -10**9
        if resources:
            for rx, ry in resources:
                my_d = dist(nx, ny, rx, ry)
                op_d = dist(ox, oy, rx, ry)
                if my_d == 0:
                    val = 100000
                else:
                    # Prefer resources I'm closer to than opponent; also bias nearer ones.
                    val = (op_d - my_d) * 3 - my_d
                if val > my_best:
                    my_best = val
        else:
            # No resources visible: move toward center while keeping distance from opponent.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            my_best = -(dist(nx, ny, cx, cy)) + dist(nx, ny, ox, oy) * 0.1

        # Small tie-break: avoid stepping into being immediately adjacent to opponent when no clear advantage.
        op_adj_pen = -2 if dist(nx, ny, ox, oy) <= 1 and (resources and my_best < 0) else 0
        score = my_best + op_adj_pen

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]