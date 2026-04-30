def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

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

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d_me = dist((sx, sy), (rx, ry))
            d_op = dist((ox, oy), (rx, ry))
            score = (d_op - d_me) * 2
            if best_score is None or score > best_score:
                best_score = score
                best = (rx, ry)
        if best is not None:
            rbx, rby = best
            # pick move that minimizes distance to best resource
            best_move = None
            best_dist = None
            for dx, dy, nx, ny in legal:
                nd = dist((nx, ny), (rbx, rby))
                if best_dist is None or nd < best_dist:
                    best_dist = nd
                    best_move = (dx, dy)
            if best_move is not None:
                return [best_move[0], best_move[1]]

    # Fallback: move toward resource cluster if any nearby, else approach center
    if resources:
        rx, ry = resources[0]
        best_move = None
        best_dist = None
        for dx, dy, nx, ny in legal:
            nd = dist((nx, ny), (rx, ry))
            if best_dist is None or nd < best_dist:
                best_dist = nd
                best_move = (dx, dy)
        if best_move is not None:
            return [best_move[0], best_move[1]]

    # If no resources considered, approach center to potentially reach future resources
    cx, cy = w // 2, h // 2
    best_move = None
    best_dist = None
    for dx, dy, nx, ny in legal:
        nd = dist((nx, ny), (cx, cy))
        if best_dist is None or nd < best_dist:
            best_dist = nd
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    return [0, 0]