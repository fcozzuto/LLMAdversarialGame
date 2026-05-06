def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", None) or []
    obstacles_raw = observation.get("obstacles", None) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources or w <= 0 or h <= 0:
        return [0, 0]

    # Choose resource maximizing opponent advantage minus our distance.
    best_r = resources[0]
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = (do - ds) * 1000 - ds
        if best_val is None or val > best_val:
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer moving closer; tie-break by reducing opponent advantage.
        score = -ds * 10 - (do - ds) * 2 + (dx == 0 and dy == 0) * -0.1
        scored.append((score, dx, dy))

    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(scored[0][1]), int(scored[0][2])]