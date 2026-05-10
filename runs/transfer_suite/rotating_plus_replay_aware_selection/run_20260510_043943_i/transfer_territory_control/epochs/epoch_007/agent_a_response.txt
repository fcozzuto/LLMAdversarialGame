def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    self_terr = observation.get("self_territory", []) or []
    opp_terr = observation.get("opponent_territory", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []

    self_set = set((p[0], p[1]) for p in self_terr if len(p) >= 2 and inb(p[0], p[1]))
    opp_set = set((p[0], p[1]) for p in opp_terr if len(p) >= 2 and inb(p[0], p[1]))
    unclaimed_set = set((p[0], p[1]) for p in unclaimed if len(p) >= 2 and inb(p[0], p[1]))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Choose a target area: nearest unclaimed if any, else nearest opponent territory
    targets = list(unclaimed_set)
    if not targets:
        targets = list(opp_set)
    if not targets:
        return [0, 0]
    tx, ty = min(targets, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))

    def score_cell(x, y):
        # Immediate claim/flip value
        s = 0.0
        if (x, y) in unclaimed_set:
            s += 3.0
        if (x, y) in opp_set:
            s += 2.8
        if (x, y) in self_set:
            s += 0.2
        # Frontier pressure: prefer cells adjacent to our territory
        adj = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self_set:
                adj += 1
        s += 0.6 * adj
        # Move-to-target pressure (small, deterministic)
        dist = abs(x - tx) + abs(y - ty)
        s -= 0.03 * dist
        # Avoid stepping into obstacle heavily
        if (x, y) in obstacles:
            s -= 1000.0
        return s

    best = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny)
        if best is None or sc > best or (sc == best and (nx, ny) < (best_move[0] + sx, best_move[1] + sy)):
            best = sc
            best_move = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]