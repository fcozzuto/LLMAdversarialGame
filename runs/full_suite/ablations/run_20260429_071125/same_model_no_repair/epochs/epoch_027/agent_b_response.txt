def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            # Prefer center while not moving toward opponent.
            key = (cheb(nx, ny, cx, cy), manh(ox, oy, nx, ny))
            # Min center distance, and then prefer larger distance from opponent.
            key = (key[0], -key[1])
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        return best

    def near_obstacle_pen(x, y):
        # Small penalty when adjacent/diagonal to obstacles.
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in occ:
                    p += 1
        return p

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        dres = min(manh(nx, ny, rx, ry) for rx, ry in resources)
        # If stepping onto a resource, strongly prefer it.
        on_res = 1 if (nx, ny) in {(rx, ry) for rx, ry in resources} else 0
        dop = manh(nx, ny, ox, oy)
        # Prefer keeping distance while progressing to resources; avoid obstacle adjacency.
        key = (0 if on_res else 1, dres, -dop, near_obstacle_pen(nx, ny), abs(nx - sx) + abs(ny - sy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]