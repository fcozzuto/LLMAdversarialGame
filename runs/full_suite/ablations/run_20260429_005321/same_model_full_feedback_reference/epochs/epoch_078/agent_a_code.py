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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = 1 if ox > sx else (-1 if ox < sx else 0)
        ty = 1 if oy > sy else (-1 if oy < sy else 0)
        for dx, dy in [(tx, ty), (tx, 0), (0, ty), (0, 0), (tx, -ty), (-tx, ty), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # One-step lookahead: choose move that maximizes the best contest score among all resources.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # From candidate position, evaluate resources using opponent-self distance difference.
        # Prefer states where we are closer (positive diff), but also prefer being closer overall.
        cur_best = -10**18
        for rx, ry in resources:
            ds = d2(nx, ny, rx, ry)
            do = d2(ox, oy, rx, ry)
            # Higher is better. Reward contest win, slightly reward shorter self distance for tie-breaking.
            val = (do - ds) * 4 - ds
            if val > cur_best:
                cur_best = val
        # Small bias toward not moving too far from current optimal direction: tie-break by immediate self distance to the best resource.
        if cur_best > best_val:
            best_val = cur_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]