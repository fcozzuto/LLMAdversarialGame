def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def obstacle_penalty(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    pen += 3
        return pen

    best_move = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            pen = obstacle_penalty(nx, ny)
            # Maximize how much closer we are than opponent to the best resource.
            best_gain = -10**18
            for rx, ry in resources:
                myd = d2(nx, ny, rx, ry)
                opd = d2(ox, oy, rx, ry)
                gain = (opd - myd) * 1000
                # discourage allowing opponent to be much closer next step too
                # (estimate by moving opponent greedily toward same resource)
                best_opp_after = 10**18
                for odx, ody in moves:
                    tox, toy = ox + odx, oy + ody
                    if not ok(tox, toy):
                        continue
                    best_opp_after = min(best_opp_after, d2(tox, toy, rx, ry))
                gain -= best_opp_after
                if gain > best_gain:
                    best_gain = gain
            val = best_gain - pen
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        tx, ty = ox, oy
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            pen = obstacle_penalty(nx, ny)
            val = -d2(nx, ny, tx, ty) * 10 - pen
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]