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
        best_move = None
        best_score = None
        for rx, ry in resources:
            d_me = dist((sx, sy), (rx, ry))
            d_op = dist((ox, oy), (rx, ry))
            score = (d_op - d_me) * 2
            if best_score is None or score > best_score:
                best_score = score
                best_move = (rx, ry)
        if best_move is not None:
            # move towards best_move selecting the first legal step that reduces distance
            tx, ty = best_move
            # choose step that minimizes distance to target
            chosen = None
            min_d = None
            for dx, dy, nx, ny in legal:
                d = dist((nx, ny), (tx, ty))
                if min_d is None or d < min_d:
                    min_d = d
                    chosen = (dx, dy)
            if chosen is not None:
                return [chosen[0], chosen[1]]

    # Fallback: move closer to opponent if no good resource grab
    best = None
    best_d = None
    for dx, dy, nx, ny in legal:
        d = dist((nx, ny), (ox, oy))
        if best_d is None or d < best_d:
            best_d = d
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    # If nothing else, stay or any legal move
    return [0, 0]