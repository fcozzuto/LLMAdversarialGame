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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = [(dx, dy) for dx, dy in moves if legal(sx + dx, sy + dy)]

    if not dirs:
        return [0, 0]

    if resources:
        # If we can grab immediately, do it.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    return [dx, dy]

        best = None
        # Score neighbor by best (small) "our distance advantage" over opponent to some resource.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            best_for_neighbor = None
            for rx, ry in resources:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                # Prefer resources close to us, far from opponent; slight bias to closer absolute ds.
                v = ds - 0.65 * do + 0.05 * ds
                if best_for_neighbor is None or v < best_for_neighbor:
                    best_for_neighbor = v
            if best is None or best_for_neighbor < best[0]:
                best = (best_for_neighbor, dx, dy)
        return [int(best[1]), int(best[2])]

    # No resources: drift toward center while keeping legal.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = md(nx, ny, cx, cy)
        if best is None or v < best[0]:
            best = (v, dx, dy)
    return [int(best[1]), int(best[2])]