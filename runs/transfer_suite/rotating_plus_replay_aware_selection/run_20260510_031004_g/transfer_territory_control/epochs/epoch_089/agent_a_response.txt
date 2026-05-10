def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    move8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    moves = move8 + [(0, 0)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    # Prefer grabbing unclaimed cells adjacent to our territory (frontier push)
    frontier = set()
    for x, y in self_terr:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and not blocked(nx, ny):
                    frontier.add((nx, ny))
    unclaimed_set = set(map(tuple, unclaimed))
    targets = [c for c in unclaimed_set if c in frontier and c not in self_terr and c not in opp_terr]
    if not targets:
        # If no frontier, target nearest unclaimed
        targets = [c for c in unclaimed_set if inb(c[0], c[1]) and not blocked(c[0], c[1])]
    if not targets:
        # Then, try to invade near our frontier into opponent territory
        targets = [c for c in opp_terr if inb(c[0], c[1]) and not blocked(c[0], c[1])]
    if not targets:
        return [0, 0]

    # Deterministic target selection
    targets.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    tx, ty = targets[0]

    # Choose a move that reduces distance to target, while avoiding obstacles
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        # Small tie-breakers: prefer moving toward center a bit and avoid opponent territory if possible
        in_opp = 1 if (nx, ny) in opp_terr else 0
        score = (dist, in_opp, abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0), dx, dy)
        if best is None or score < best[0]:
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]