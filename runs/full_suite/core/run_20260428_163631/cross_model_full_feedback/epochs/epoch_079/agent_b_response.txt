def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

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

    # Target closest resource if ahead of opponent; else head to center to threaten multiple
    target = None
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d_me = dist((sx, sy), (rx, ry))
            d_op = dist((ox, oy), (rx, ry))
            score = (d_op - d_me) * 2  # favor nearer to resource than opponent
            if best_score is None or score > best_score:
                best_score = score
                best = (rx, ry)
        target = best

    def toward(target_xy):
        tx, ty = target_xy
        # choose move reducing manhattan distance
        best_move = None
        best_diff = None
        for dx, dy, nx, ny in legal:
            d = dist((nx, ny), (tx, ty))
            if best_diff is None or d < best_diff:
                best_diff = d
                best_move = (dx, dy)
        if best_move is None:
            return (0, 0)
        return best_move

    if target is not None:
        move = toward(target)
        if move is not None:
            return [int(move[0]), int(move[1])]

    # If no resource pursued, simple approach: move away from opponent a bit if possible, else towards center
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        # prefer moves that increase distance from opponent
        d_op = dist((nx, ny), (ox, oy))
        if best_score is None or d_op > best_score:
            best_score = d_op
            best_move = (dx, dy)
    if best_move is not None:
        return [int(best_move[0]), int(best_move[1])]

    return [0, 0]