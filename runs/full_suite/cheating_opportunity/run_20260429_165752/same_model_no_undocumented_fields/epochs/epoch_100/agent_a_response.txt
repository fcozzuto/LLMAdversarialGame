def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in moves:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_val = None

    # If there are no visible resources, just drift toward the board center while keeping safe.
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = (abs(nx - tx) + abs(ny - ty)) - 0.1 * cheb(nx, ny, ox, oy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Evaluate how good our next position is: prioritize resources we can reach sooner than the opponent.
        min_cost = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Lower is better: reach sooner, and where opponent is slower.
            cost = ds - 0.55 * do
            # Small tie-break: prefer being closer to the resource absolute.
            cost += 0.01 * ds
            if min_cost is None or cost < min_cost:
                min_cost = cost
        # Secondary tie-break: also try not to give opponent an immediate swing.
        tie = 0.02 * cheb(nx, ny, ox, oy)
        val = min_cost + tie
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move