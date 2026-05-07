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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    def best_value(px, py):
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive => we reach first
            # Prefer higher lead, then closer to resource, then slightly more distant from opponent
            key = (lead, -ds, do, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        return best[0]

    best_move = None
    best_key = None
    for dx, dy, nx, ny in legal_moves:
        key = best_value(nx, ny)
        # Small bias toward staying aligned with the opponent's likely pressure:
        # if we can capture with a lead, keep improving; otherwise reduce distance gap to top target.
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]