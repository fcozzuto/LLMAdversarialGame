def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp:
                    return True
        return False

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target unclaimed cell that is adjacent to opponent territory (edge-claim counter)
    best_t = None
    best_score = -10**18
    for ux, uy in un:
        if not adj_to_opp(ux, uy):
            continue
        edge = (ux == 0 or uy == 0 or ux == w - 1 or uy == h - 1)
        d = man((sx, sy), (ux, uy))
        sc = 500 - 3 * d + (50 if edge else 0)
        if sc > best_score:
            best_score = sc
            best_t = (ux, uy)

    # Fallback: nearest unclaimed on edges
    if best_t is None:
        edge_un = [(x, y) for (x, y) in un if (x == 0 or y == 0 or x == w - 1 or y == h - 1)]
        if edge_un:
            best_t = min(edge_un, key=lambda p: man((sx, sy), p))
        elif un:
            best_t = min(un, key=lambda p: man((sx, sy), p))
        else:
            # Last resort: head toward center to avoid being outflanked on edges
            best_t = (w // 2, h // 2)

    tx, ty = best_t

    # Evaluate immediate move by local gain potential
    best_move = [0, 0]
    best_move_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell_score = 0
        if (nx, ny) in un:
            cell_score += 120
            if adj_to_opp(nx, ny):
                cell_score += 80
            if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
                cell_score += 30
        if (nx, ny) in opp:
            cell_score += 260  # entering opponent-owned flips control (high value)
        if (nx, ny) in selft:
            cell_score += 10  # don't run away unnecessarily

        # Positioning: reduce distance to the chosen target, but prefer not to drift onto edges unless targeting
        dist = man((nx, ny), (tx, ty))
        pos_score = -6 * dist

        # Mild anti-stall: prefer moves that change location unless clearly best
        move_pen = -2 if (dx == 0 and dy == 0) else 0

        total = cell_score + pos_score + move_pen
        if total > best_move_score:
            best_move_score = total
            best_move = [dx, dy]

    return best_move