def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def danger(x, y):
        # Penalize being adjacent (8-neighborhood) to obstacles to reduce getting trapped.
        c = 0
        for dxx, dyy in deltas:
            tx, ty = x + dxx, y + dyy
            if (tx, ty) in obstacles:
                c += 1
        return c

    # If no resources, move to maximize distance from opponent (deterministic).
    if not resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = dist((nx, ny), (ox, oy)) - 0.5 * danger(nx, ny)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose move that creates the largest advantage on the most contestable resource.
    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        dme = dist((nx, ny), (ox, oy))  # small tie-breaker component
        local_best = None
        for rx, ry in resources:
            d_me = dist((nx, ny), (rx, ry))
            d_op = dist((ox, oy), (rx, ry))
            # High when we are closer than opponent; also prefer closer targets.
            val = (d_op - d_me) * 2 - d_me * 0.15 - danger(nx, ny) * 0.25
            if local_best is None or val > local_best:
                local_best = val
        # Prefer moves that also slightly increase separation from opponent.
        v = local_best + dme * 0.02
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]