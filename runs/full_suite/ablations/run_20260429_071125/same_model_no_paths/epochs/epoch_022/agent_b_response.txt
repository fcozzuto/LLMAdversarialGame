def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def nearest_target(x, y):
        if not resources:
            return None
        best = None
        bestd = None
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if bestd is None or d < bestd or (d == bestd and (rx, ry) < best):
                bestd = d
                best = (rx, ry)
        return best

    target = nearest_target(sx, sy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if target is None:
            dres = 0
            tpen = 0
        else:
            dres = cheb(nx, ny, target[0], target[1])
            tpen = 0
            for rx, ry in resources:
                if (rx, ry) == target:
                    continue
                if cheb(nx, ny, rx, ry) == dres:
                    tpen += 1  # deterministic preference among equal-distance options

        dop = cheb(nx, ny, ox, oy)
        if target is not None:
            # Encourage moves that reduce our distance to target but keep opponent farther.
            val = (-(dres * 10 + tpen), -(dop), dx, dy)
        else:
            val = (-(dop * 5), dx, dy)

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]