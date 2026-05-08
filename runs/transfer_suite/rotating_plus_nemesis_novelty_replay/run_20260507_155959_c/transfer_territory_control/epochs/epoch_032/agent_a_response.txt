def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []
    unclaimed = [(int(x), int(y)) for x, y in unclaimed if 0 <= int(x) < w and 0 <= int(y) < h]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx + dy

    # Precompute nearest unclaimed distances from current position (lightweight)
    if unclaimed:
        # Deterministic: tie-break by (dist, y, x)
        nearest = min(unclaimed, key=lambda t: (man((sx, sy), t), t[1], t[0]))
    else:
        nearest = None

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        score = 0

        if cell in opp_cells:
            score += 10000  # flipping on entry is strong
            # Prefer approaching opponent territory boundary nearer to us
            score += -man((nx, ny), (ox, oy))
        elif cell in self_cells:
            score += 3  # keep momentum
        else:
            # If unclaimed, prefer expansion towards nearest frontier
            if cell not in self_cells and cell not in opp_cells:
                score += 50 if nearest is None else max(0, 20 - (man((nx, ny), nearest)))
                score += -man((nx, ny), nearest) if nearest is not None else 0

        # Avoid moving too close to opponent unless flipping
        if cell not in opp_cells:
            dist_to_opp = man((nx, ny), (ox, oy))
            score += dist_to_opp  # farther is safer

        # Deterministic tie-break: prefer smaller (dx,dy) ordering via fixed iteration + score only
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]