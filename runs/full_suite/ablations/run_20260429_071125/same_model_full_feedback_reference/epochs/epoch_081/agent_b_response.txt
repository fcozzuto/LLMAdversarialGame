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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_move = (0, 0)

    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
                dx, dy = 0, 0
            best_adv = -10**9
            best_sd = 10**9
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                od_d = cheb(ox, oy, rx, ry)
                adv = od_d - my_d
                if adv > best_adv or (adv == best_adv and my_d < best_sd):
                    best_adv = adv
                    best_sd = my_d
            # secondary: prefer being closer to the chosen resource set
            val = best_adv * 1000 - best_sd
            cand = (val, dx, dy)
            if best is None or cand > best:
                best = cand
                best_move = (dx, dy)
    else:
        # No resources visible: head to center while keeping some distance from opponent
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
                dx, dy = 0, 0
            cdist = abs(nx - center_x) + abs(ny - center_y)
            odist = cheb(nx, ny, ox, oy)
            val = -cdist + odist * 0.1
            cand = (val, dx, dy)
            if best is None or cand > best:
                best = cand
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]