def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if o is not None and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_primary = None
    best_secondary = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_best = None
        my_tieb = None
        for rx, ry in resources:
            od = cheb(ox, oy, rx, ry)
            md = cheb(nx, ny, rx, ry)
            # primary: maximize lead over opponent; secondary: prefer closer resource
            primary = od - md
            secondary = md
            if my_best is None or primary > my_best or (primary == my_best and secondary < my_tieb):
                my_best = primary
                my_tieb = secondary
        if my_best is None:
            continue
        if best_primary is None or my_best > best_primary or (my_best == best_primary and (my_tieb < best_secondary)):
            best_primary, best_secondary = my_best, my_tieb
            best_move = (dx, dy)
        elif my_best == best_primary and my_tieb == best_secondary:
            # deterministic tie-break: lexicographically smallest move
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]