def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and valid(x, y):
                resources.append((x, y))

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    if resources:
        def dist(x, y):
            dx = x - sx
            if dx < 0: dx = -dx
            dy = y - sy
            if dy < 0: dy = -dy
            return dx + dy

        resources.sort(key=lambda t: (dist(t[0], t[1]), t[1], t[0]))
        tx, ty = resources[0]

        best = None
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best is not None else [0, 0]

    ox = oy = None
    op = observation.get("opponent_position")
    if isinstance(op, (list, tuple)) and len(op) >= 2:
        ox, oy = int(op[0]), int(op[1])

    if ox is not None and oy is not None and 0 <= ox < w and 0 <= oy < h:
        def oppdist(dx, dy):
            nx, ny = sx + dx, sy + dy
            return abs(nx - ox) + abs(ny - oy)

        best = None
        bestd = -1
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = oppdist(dx, dy)
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best is not None else [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]