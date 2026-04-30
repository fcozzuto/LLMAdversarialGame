def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    target = None
    best = -10**18
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Prefer resources we're closer to; strongly penalize ones opponent is already closer to.
        score = (do - ds) * 10 - ds
        if do < ds:
            score -= 50 + (ds - do)
        # Deterministic tie-break by coordinates
        if score > best or (score == best and (x, y) < target):
            best = score
            target = (x, y)

    if target is None:
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = target

    # Choose move that reduces distance to target; if blocked, pick best alternative.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Also prefer not to step into positions that let opponent "gain" on the same target.
        val = (do - ds) * 10 - ds - (0.5 if dx == 0 and dy == 0 else 0)
        if dx == 0 and dy == 0:
            val -= 1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]