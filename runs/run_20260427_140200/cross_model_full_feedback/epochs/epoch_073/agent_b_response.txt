def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    if not resources:
        # If no resources visible, move toward center while avoiding obstacles
        cx, cy = w//2, h//2
        best = None
        bestd = None
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not inb(nx, ny):
                continue
            d = max(abs(nx - cx), abs(ny - cy))
            if bestd is None or d < bestd or (d == bestd and (nx, ny) < best):
                best = (nx, ny)
                bestd = d
        if best is None:
            return [0, 0]
        return [best[0]-mx, best[1]-my]

    # There are resources: choose nearest resource deterministically, tie-break by coordinates
    best_r = None
    best_dist = None
    for r in resources:
        d = cheb((mx, my), r)
        if best_dist is None or d < best_dist or (d == best_dist and r < best_r):
            best_r = r
            best_dist = d

    if best_r is None:
        return [0, 0]

    # Move greedily toward best_r, avoid obstacles, stay within grid
    dx = 0
    dy = 0
    if best_r[0] > mx: dx = 1
    elif best_r[0] < mx: dx = -1
    if best_r[1] > my: dy = 1
    elif best_r[1] < my: dy = -1

    nx, ny = mx + dx, my + dy
    if inb(nx, ny):
        return [dx, dy]

    # If blocked, try alternative moves ordered by closeness to resource
    cand = []
    for mx2, my2 in moves:
        nx, ny = mx + mx2, my + my2
        if inb(nx, ny):
            d = cheb((nx, ny), best_r)
            cand.append(((mx2, my2), d))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (t[1], t[0]))
    return [cand[0][0][0], cand[0][0][1]]