def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    best = None
    for r in resources:
        x, y = int(r[0]), int(r[1])
        if (x, y) in obstacles:
            continue
        ds = dist_cheb(sx, sy, x, y)
        do = dist_cheb(ox, oy, x, y)
        if do < ds:  # likely opponent can take it first; deprioritize
            continue
        # Prefer resources that are "more ours" and not too close to opponent
        corner_bias = (x in (0, w - 1)) + (y in (0, h - 1))
        value = ds + 0.35 * (8 - do) - 0.15 * corner_bias
        if best is None or value < best:
            best = value
            target = (x, y)

    if target is None:
        # Fallback: pick any in-bounds resource (deterministic)
        for r in resources:
            x, y = int(r[0]), int(r[1])
            if (x, y) in obstacles:
                continue
            ds = dist_cheb(sx, sy, x, y)
            do = dist_cheb(ox, oy, x, y)
            value = ds - 0.25 * do
            if best is None or value < best:
                best = value
                target = (x, y)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    tx, ty = target if target is not None else (sx, sy)
    cur = (sx, sy)
    opp = (ox, oy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = dist_cheb(nx, ny, tx, ty)
        do = dist_cheb(nx, ny, opp[0], opp[1])
        # Greedy progress with anti-trap: avoid getting too close to opponent while moving toward target
        score = ds + 0.10 * max(0, 4 - do) - 0.01 * ((nx in (0, w - 1)) + (ny in (0, h - 1)))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]