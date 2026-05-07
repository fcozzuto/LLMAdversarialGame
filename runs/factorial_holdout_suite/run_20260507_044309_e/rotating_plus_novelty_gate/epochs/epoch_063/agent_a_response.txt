def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # Prefer moving to the corner farthest from opponent (likely to secure last resources).
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        best = None
        best_key = None
        for dx, dy, nx, ny in valid:
            k = (cheb(nx, ny, tx, ty), dx, dy)
            if best_key is None or k < best_key:
                best_key = k
                best = (dx, dy)
        return [best[0], best[1]]

    # For each move, choose the single best target resource for us, then maximize advantage over opponent.
    resources_sorted = sorted(resources, key=lambda r: (cheb(r[0], r[1], sx, sy), r[0], r[1]))
    best_move = (0, 0)
    best_key = None

    for dx, dy, nx, ny in valid:
        # immediate collection: if resource at (nx,ny), prefer strongly
        collect_bonus = 1000 if any(r[0] == nx and r[1] == ny for r in resources) else 0

        # pick our best resource (closest after move; deterministic tie-break)
        best_r = None
        best_r_key = None
        for rx, ry in resources_sorted:
            k = (cheb(nx, ny, rx, ry), rx, ry)
            if best_r_key is None or k < best_r_key:
                best_r_key = k
                best_r = (rx, ry)
                break

        rx, ry = best_r
        self_dist = cheb(nx, ny, rx, ry)
        opp_dist = cheb(ox, oy, rx, ry)
        # maximize opponent delay relative to us; also mildly prefer smaller self_dist to finish sooner
        score_key = (-(opp_dist - self_dist) - collect_bonus, self_dist, -opp_dist, dx, dy)
        if best_key is None or score_key < best_key:
            best_key = score_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]