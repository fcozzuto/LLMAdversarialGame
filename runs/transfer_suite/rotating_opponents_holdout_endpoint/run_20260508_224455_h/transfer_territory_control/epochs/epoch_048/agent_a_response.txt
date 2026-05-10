def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for c in observation.get("obstacles", []) or []:
        if c is not None and len(c) >= 2:
            x, y = c[0], c[1]
            if x is not None and y is not None:
                obstacles.add((int(x), int(y)))

    self_set = set(tuple(map(int, p)) for p in (observation.get("self_territory", []) or []))
    opp_set = set(tuple(map(int, p)) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(map(int, p)) for p in (observation.get("unclaimed_cells", []) or []))

    px, py = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    px, py = int(px), int(py)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist_to_center(x, y):
        dx, dy = x - cx, y - cy
        return (dx * dx + dy * dy) ** 0.5

    def dist_manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    sc0 = float(dist_to_center(sx, sy))
    fo0 = float(dist_manh(sx, sy, px, py))

    best = [0, 0]
    best_sc = -1e18
    # deterministic tie-breaker order: dirs order, then lower lex (dx,dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_set:
            base = 120.0
        elif (nx, ny) in unclaimed:
            base = 35.0
        elif (nx, ny) in self_set:
            base = 7.0
        else:
            base = 18.0

        sc = base
        sc += 4.0 * (sc0 - dist_to_center(nx, ny))  # move toward center
        sc += 1.5 * (fo0 - dist_manh(nx, ny, px, py))  # move toward opponent
        if dx == 0 and dy == 0:
            sc -= 3.0  # prefer moving

        if sc > best_sc or (sc == best_sc and (dx, dy) < (best[0], best[1])):
            best_sc = sc
            best = [dx, dy]

    return [int(best[0]), int(best[1])]