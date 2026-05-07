def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, dict):
            x = p.get("x", None); y = p.get("y", None)
            if x is not None and y is not None:
                obstacles.add((int(x), int(y)))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, dict):
            x = r.get("x", None); y = r.get("y", None)
            if x is not None and y is not None:
                resources.append((int(x), int(y)))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources:
        return [0, 0]

    # Greedy step toward the resource we can secure earlier than opponent.
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        ax = a - c; ax = -ax if ax < 0 else ax
        by = b - d; by = -by if by < 0 else by
        return ax + by

    # Prefer resources that are either closer than opponent, or otherwise overall closest.
    best_delta = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine keeps us in place on invalid moves
        # Evaluate the best target given this next position.
        cur_best = None
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # Lower is better. Strongly favor taking positions we reach earlier.
            val = (ds - do) * 2 + ds
            # Small tie-break to favor picking up closer resources quickly.
            if cur_best is None or val < cur_best:
                cur_best = val
        # Higher is better for move selection: invert.
        move_val = -cur_best
        if best_val is None or move_val > best_val:
            best_val = move_val
            best_delta = [dx, dy]

    return [int(best_delta[0]), int(best_delta[1])]