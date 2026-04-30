def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def obstacle_prox(x, y):
        best = 10
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best if best != 10 else 99

    lm = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            lm.append((dx, dy, nx, ny))
    if not lm:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in lm:
            key = (cheb(nx, ny, tx, ty), -min(obstacle_prox(nx, ny), 3), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Pick a resource we can reach relatively earlier than the opponent.
    best_res = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        # Tie-break: prefer closer resources to reduce pathing ambiguity.
        key = (-lead, ds, rx, ry)
        if best_res is None or key < best_res[0]:
            best_res = (key, (rx, ry))
    tr, ty = best_res[1]

    # Evaluate moves: minimize distance to chosen target, keep away from obstacles, and
    # slightly prefer increasing lead against opponent for that same target.
    best = None
    for dx, dy, nx, ny in lm:
        ds_next = cheb(nx, ny, tr, ty)
        do = cheb(ox, oy, tr, ty)
        lead_next = do - ds_next
        prox = obstacle_prox(nx, ny)
        # Prefer higher lead; for determinism use integer-tuple ordering.
        key = (-lead_next, ds_next, -(min(prox, 4)), cheb(nx, ny, (w - 1) // 2, (h - 1) // 2), dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]