def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and ok(x, y):
                sd = cheb(sx, sy, x, y)
                od = cheb(ox, oy, x, y)
                valid.append((x, y, sd, od))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_step = (0, 0)
    best_score = None

    if not valid:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Prefer steps that let us be earlier than opponent on some resource.
        step_best = None
        for x, y, sd, od in valid:
            nsd = cheb(nx, ny, x, y)
            # Higher score is better: earlier self, and avoid giving opponent advantage.
            # Use integer-safe lex ordering.
            delta = (od - nsd)  # positive if we are closer/tighter than opponent
            tie = (x, y)
            cand = (delta, -nsd, -cheb(ox, oy, x, y), tie)
            if step_best is None or cand > step_best:
                step_best = cand
        score = step_best
        if best_score is None or score > best_score:
            best_score = score
            best_step = (dx, dy)

    return [best_step[0], best_step[1]]