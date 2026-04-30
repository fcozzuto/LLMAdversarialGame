def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a; bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # Choose target: nearest resource; tie-break deterministically by (x,y).
    if resources:
        target = min(resources, key=lambda r: (dist((sx, sy), r), r[0], r[1]))
    else:
        # No visible resources: head toward center-ish for safety/contestion avoidance.
        target = (w // 2, h // 2)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Heuristic: reduce distance to target; penalize being adjacent to obstacles;
        # and prefer moves that don't immediately trap (look one more step).
        d1 = abs(nx - target[0]) + abs(ny - target[1])

        adj_pen = 0
        for ox, oy in [(nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1),
                       (nx+1, ny+1), (nx+1, ny-1), (nx-1, ny+1), (nx-1, ny-1)]:
            if inb(ox, oy) and (ox, oy) in obstacles:
                adj_pen += 1

        trap = 0
        # If next-step options are few because of obstacles, penalize.
        free_next = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) not in obstacles:
                free_next += 1
        if free_next <= 2:
            trap = 3

        # Slight deterministic preference to move east/north when equal.
        dir_pref = 0
        if dx > 0: dir_pref -= 0.01
        if dy > 0: dir_pref -= 0.005

        score = (d1, adj_pen, trap, dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]