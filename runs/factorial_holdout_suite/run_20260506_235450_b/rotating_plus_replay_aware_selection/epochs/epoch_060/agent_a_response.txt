def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    legal_deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in legal_deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not resources or not legal:
        return [0, 0]

    best_t = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds <= do:
            key = (1, do - ds, -ds, -do, rx, ry)  # race win / denial backup
        else:
            key = (0, -do, -(ds - do), -ds, rx, ry)  # contest opponent's closest threats
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    best = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        d = cheb(nx, ny, tx, ty)
        # Also nudge to reduce opponent's ability by moving toward our target while not worsening relative distance to it too much
        do_next = cheb(ox, oy, tx, ty)
        rel = d - do_next
        key = (-d, rel, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]