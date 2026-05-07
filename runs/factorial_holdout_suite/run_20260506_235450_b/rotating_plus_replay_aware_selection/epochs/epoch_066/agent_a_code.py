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

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not resources or not legal:
        return [0, 0]

    best_move = (0, 0)
    best_key = None

    # Deterministic ordering when keys match: prefer smaller (dx,dy) lexicographically.
    for dx, dy, nx, ny in legal:
        # For this move, find the best resource to target (race/denial).
        move_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # Win if we can arrive strictly no later than opponent; tie-break by larger margin,
            # then by smaller our distance (faster collection), then by smaller opponent distance.
            if ds <= do:
                # winFlag=1, prefer larger (do-ds), then smaller ds (via -ds), then smaller do
                key = (1, do - ds, -ds, -do, -rx, -ry)
            else:
                # Denial: choose move maximizing (do-ds) (opponent farther from the resource)
                # while keeping our distance as small as possible.
                key = (0, do - ds, -ds, -do, -rx, -ry)

            if move_key is None or key > move_key:
                move_key = key

        if best_key is None or move_key > best_key or (move_key == best_key and (dx, dy) < best_move):
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]