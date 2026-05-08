def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or not inb(x, y)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    role = (observation.get("self_role") or "").lower()
    self_is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("coward" in role)

    if not self_is_evader:
        best_d = None
        best = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if best_d is None or d < best_d or (d == best_d and (dx, dy) < best):
                best_d = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = None
    best_corner_score = None
    for cx, cy in corners:
        if blocked(cx, cy):
            continue
        # Prefer corners farthest from pursuer; tie-break by also farthest from self (avoid suicidal moves into obstacles)
        corner_score = cheb(ox, oy, cx, cy)
        if best_corner_score is None or corner_score > best_corner_score:
            best_corner_score = corner_score
            best_corner = (cx, cy)
    if best_corner is None:
        best_corner = (0, 0)

    tx, ty = best_corner
    best = (0, 0)
    best_tuple = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)     # maximize
        d_tgt = cheb(nx, ny, tx, ty)    # then minimize
        # Deterministic tie-breaker by lexicographic (dx,dy)
        t = (-d_opp, d_tgt, dx, dy)
        if best_tuple is None or t < best_tuple:
            best_tuple = t
            best = (dx, dy)
    return [int(best[0]), int(best[1])]