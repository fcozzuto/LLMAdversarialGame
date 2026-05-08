def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_near = 0
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        if (ox + dx, oy + dy) in selfT:
            opp_near += 1

    best = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_opp = abs(nx - ox) + abs(ny - oy)

        base = 0
        if cell in unclaimed:
            base += 6
        elif cell in oppT:
            base += 4
        elif cell in selfT:
            base += 2
        else:
            base += 1

        # Prefer expansion toward center and away from opponent pressure
        score = base
        score += (14 - dist_center) * 0.35
        score += (10 - dist_opp) * (-0.25)

        # If we step adjacent to opponent, value it only if it captures territory
        adj_to_opp = dist_opp <= 2
        if adj_to_opp:
            score += 1.5 if (cell in unclaimed or cell in oppT) else -2.0

        # Mild anti-loop: discourage returning to positions with no nearby unclaimed/opp
        if cell in selfT:
            neighbor_open = 0
            for tx in (-1, 0, 1):
                for ty in (-1, 0, 1):
                    if tx == 0 and ty == 0:
                        continue
                    px, py = nx + tx, ny + ty
                    if not inb(px, py):
                        continue
                    if (px, py) in unclaimed or (px, py) in oppT:
                        neighbor_open += 1
            score += neighbor_open * 0.6 - opp_near * 0.05

        if score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]