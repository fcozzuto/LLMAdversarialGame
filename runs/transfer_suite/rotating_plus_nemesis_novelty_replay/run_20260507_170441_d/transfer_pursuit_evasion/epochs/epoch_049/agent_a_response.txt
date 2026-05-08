def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("pursuer" in self_role) and ("evader" not in self_role)
    if ("pursuer" in opp_role) and ("evader" in self_role):
        self_is_pursuer = False

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def open_neighbors(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    # Evaluate candidate moves (stay if blocked)
    best_move = [0, 0]
    if self_is_pursuer:
        # Chase: minimize distance; prefer mobility; avoid moving onto/through obstacles handled by free()
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            dist = cheb(nx, ny, ox, oy)
            mob = open_neighbors(nx, ny)
            key = (dist, -mob, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
    else:
        # Evade: maximize distance; if tie, maximize mobility; also bias toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            dist = cheb(nx, ny, ox, oy)
            mob = open_neighbors(nx, ny)
            center_bias = -(abs(nx - cx) + abs(ny - cy))  # closer to center => larger
            key = (-dist, -mob, -center_bias, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]