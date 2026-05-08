def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    self_role = observation.get("self_role", "") or ""
    pursuer = ("purs" in self_role.lower())  # deterministic role detection

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # If our start is somehow blocked, do nothing (engine will keep us in place if invalid).
    if (sx, sy) in obstacles:
        return [0, 0]

    best_move = [0, 0]
    # For pursuer: minimize distance. For evader: maximize distance.
    # Tie-breaker: prefer moves that also keep within bounds and don't step on obstacles.
    target_dist = manh(sx, sy, ox, oy)
    if pursuer:
        best_key = (target_dist, 0, 0)
    else:
        best_key = (-target_dist, 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        # Capture radius is 0; capture when d == 0.
        # Pursuer wants d -> 0; evader wants d -> large.
        if pursuer:
            key = (d, (dx == 0 and dy == 0), abs(nx - ox) + abs(ny - oy))
            if key < best_key:
                best_key = key
                best_move = [dx, dy]
        else:
            key = (-d, (dx == 0 and dy == 0), abs(nx - ox) + abs(ny - oy))
            if key < best_key:
                best_key = key
                best_move = [dx, dy]

    return best_move