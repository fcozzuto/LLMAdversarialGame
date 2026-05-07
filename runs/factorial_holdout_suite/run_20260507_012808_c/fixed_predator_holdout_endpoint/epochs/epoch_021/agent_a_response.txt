def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if resources:
        # Choose a resource where we are not only closer, but the advantage is biggest.
        best_cell = None
        best_key = None
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            # Prefer (opponent farther than us), then smaller own distance, then stable tie-break.
            key = (do - ds, -ds, rx + 97 * ry)
            if best_key is None or key > best_key:
                best_key, best_cell = key, (rx, ry)

        rx, ry = best_cell
        tx = 0 if rx == sx else (1 if rx > sx else -1)
        ty = 0 if ry == sy else (1 if ry > sy else -1)

        # Prefer diagonal/combined step if it moves toward target and is legal.
        candidates = [(tx, ty)]
        if (tx, 0) != (tx, ty):
            candidates.append((tx, 0))
        if (0, ty) != (tx, ty):
            candidates.append((0, ty))
        candidates.append((tx, ty if ty != 0 else 0))

        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]

    # Fallback: move to maximize "opponent gets less advantage" among reachable neighbors.
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if resources:
            # Use current best resource heuristic but based on neighbor position.
            key1 = None
            for rx, ry in resources:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                key = (do - ds, -ds, rx + 97 * ry)
                if key1 is None or key > key1:
                    key1 = key
            key = key1
        else:
            # If no resources, keep distance from opponent deterministically.
            key = (-md(nx, ny, ox, oy), nx + 97 * ny)
        if best_key is None or key > best_key:
            best_key, best = key, (dx, dy)
    return [int(best[0]), int(best[1])]