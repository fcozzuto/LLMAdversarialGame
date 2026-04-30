def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Pick best target resource: prioritize being earlier than opponent.
    best_t = None
    best = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        ahead = do - ds  # positive if we are sooner
        # tie-break toward closer-to-us and farther-from-opp (more likely stable advantage)
        score = ahead * 100 - ds * 3 + do
        if best is None or score > best_t:
            best_t = score
            best = (rx, ry)

    tx, ty = best
    best_move = (0, 0)
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        # Move that reduces distance to target; keep advantage if possible.
        evalv = (do2 - ds2) * 100 - ds2 * 3
        # Slight preference to not drift too far when equal
        evalv -= (md(nx, ny, sx, sy) * 0.01)
        if best_eval is None or evalv > best_eval:
            best_eval = evalv
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]