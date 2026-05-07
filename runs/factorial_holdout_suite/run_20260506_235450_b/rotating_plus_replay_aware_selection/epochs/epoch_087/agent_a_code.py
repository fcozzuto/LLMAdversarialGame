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

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal or not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        lead = do - ds  # positive means we can reach earlier
        # Prefer strong lead, then closer distance to ensure quick pickup.
        key = (lead, -ds)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # If currently on a resource, just stay (deterministic).
    if (sx, sy) == (rx, ry):
        return [0, 0]

    # Move that minimizes distance to target while keeping a good "race" against opponent.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        ds_next = man(nx, ny, rx, ry)
        do = man(ox, oy, rx, ry)
        lead_next = do - ds_next
        score = (lead_next, -ds_next)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]