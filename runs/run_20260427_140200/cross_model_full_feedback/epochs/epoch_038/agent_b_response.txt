def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
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
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Deterministic heuristic:
    # 1) If there is a resource, move toward the closest one.
    # 2) If no resource or after moving toward resource, slightly favor moving away from opponent
    #    to maximize space for future turns, but stay within board and not on obstacle.
    best_dx = 0
    best_dy = 0
    best_score = None

    if resources:
        # pick closest resource
        target = None
        best_r = None
        for rx, ry in resources:
            d = man(sx, sy, rx, ry)
            if best_r is None or d < best_r:
                best_r = d
                target = (rx, ry)
        tx, ty = target
        # choose move that reduces distance to target, break ties deterministically by dx,dy order
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if best_score is None or d < best_score or (d == best_score and (dx, dy) < (best_dx, best_dy)):
                best_score = d
                best_dx, best_dy = dx, dy
        return [best_dx, best_dy]

    # No resources: maintain space by moving away from opponent if possible, else stay
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # prefer further from opponent
        d = man(nx, ny, ox, oy)
        if best_score is None or d > best_score or (d == best_score and (dx, dy) < (best_dx, best_dy)):
            best_score = d
            best_dx, best_dy = dx, dy

    # Fallback if no legal move (should not happen on 8x8 with 2 obstacles)
    return [best_dx, best_dy]