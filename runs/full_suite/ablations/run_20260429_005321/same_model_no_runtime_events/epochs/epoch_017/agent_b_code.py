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

    deltas = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        x1, y1 = a
        x2, y2 = b
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    blocked = set(deltas)
    if not resources:
        tx, ty = (ox, oy)
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                d = dist((nx, ny), (tx, ty))
                if best is None or d < best[0]:
                    best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        md = min(dist((nx, ny), r) for r in resources)
        if best is None or md < best[0]:
            best = (md, dx, dy)
        elif best is not None and md == best[0]:
            if (dx, dy) == (0, 0) and best[1:3] != (0, 0):
                pass
            elif (dx, dy) == (0, 0):
                pass
            else:
                best = (md, dx, dy)

    return [best[1], best[2]] if best else [0, 0]