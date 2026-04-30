def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))

    def to_xy(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return (int(p[0]), int(p[1]))
        if isinstance(p, dict) and "x" in p and "y" in p:
            return (int(p["x"]), int(p["y"]))
        return None

    obstacles = set()
    for p in observation.get("obstacles") or []:
        q = to_xy(p)
        if q is not None:
            obstacles.add(q)

    resources = []
    for p in observation.get("resources") or []:
        q = to_xy(p)
        if q is not None and q not in obstacles:
            resources.append(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
        bx = max(0, min(w-1, sx))
        by = max(0, min(h-1, sy))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    # Pick target: prefer resources we can reach earlier than opponent, tie-break deterministically.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Higher ds advantage is better (opponent farther), so use key to minimize negative.
        key = (-(do - ds), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Local evaluation: closer to target, avoid enabling opponent capture.
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)  # opponent static this turn
        # Also discourage stepping into squares that reduce our path vs opponent too much next to obstacles a bit.
        # Deterministic tie-break by dx,dy ordering.
        score = (my_d, -(op_d - my_d), dx * 10 + dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]