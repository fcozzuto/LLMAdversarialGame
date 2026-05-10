def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        try:
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d = cheb(nx, ny, ox, oy)

        # Greedy obstacle-avoidance: prefer moving to cells with more free neighbors.
        free = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) not in obstacles:
                free += 1

        # Small tie-break to stabilize behavior and reduce dithering.
        tie = cheb(nx, ny, w - 1, h - 1) + 0.001 * (nx + ny)

        if is_evader:
            score = d * 10.0 + free * 0.2 - tie
        else:
            score = -d * 10.0 + free * 0.2 - tie

        if best_score is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]