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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        best = [0, 0]
        bestk = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            k = (cheb(nx, ny, ox, oy), nx, ny)
            if k > bestk:
                bestk = k
                best = [dx, dy]
        return best

    # Prefer shortest path to the nearest resource; if equal, prefer moving away from opponent.
    # If multiple resources tie, break by resource coordinate for determinism.
    resources_sorted = sorted(resources)
    best = [0, 0]
    bestk = (-10**9, -10**9, 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        nearest_d = 10**9
        nearest_r = resources_sorted[0]
        for rx, ry in resources_sorted:
            d = cheb(nx, ny, rx, ry)
            if d < nearest_d:
                nearest_d = d
                nearest_r = (rx, ry)
            elif d == nearest_d and (rx, ry) < nearest_r:
                nearest_r = (rx, ry)

        opp_d = cheb(nx, ny, ox, oy)
        on_res = 1 if (nx, ny) in obstacles else 0
        on_res = 1 if (nx, ny) in set(resources) else 0  # deterministic

        # Higher is better
        key = (on_res, -nearest_d, opp_d, -cheb(nx, ny, nearest_r[0], nearest_r[1]))
        if key > bestk:
            bestk = key
            best = [dx, dy]

    return best