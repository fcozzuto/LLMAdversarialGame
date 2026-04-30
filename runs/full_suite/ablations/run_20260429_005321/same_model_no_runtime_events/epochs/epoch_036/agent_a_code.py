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
    res_set = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if -d > best[2]:
                best = (dx, dy, -d)
        return [best[0], best[1]]

    resources_sorted = sorted(resources, key=lambda t: (t[0], t[1]))
    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in res_set:
            my_d = 0
            op_best = 0
            op_to = []
            for (rx, ry) in resources_sorted:
                op_to.append(cheb(ox, oy, rx, ry))
            op_best = min(op_to) if op_to else 0
            val = 1000000 + op_best
        else:
            my_min = 10**9
            op_min = 10**9
            for (rx, ry) in resources_sorted:
                dmy = cheb(nx, ny, rx, ry)
                if dmy < my_min:
                    my_min = dmy
                dop = cheb(ox, oy, rx, ry)
                if dop < op_min:
                    op_min = dop
            val = (op_min * 1000) - (my_min * 120)

            # small tie-break toward central-ish and toward current best target
            center_dist = cheb(nx, ny, (w - 1) / 2, (h - 1) / 2)
            val -= int(center_dist * 10)

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]