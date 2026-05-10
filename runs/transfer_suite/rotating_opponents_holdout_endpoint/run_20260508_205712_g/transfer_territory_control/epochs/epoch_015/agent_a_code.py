def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    oppT = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oppT.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Targets: prioritize nearest opponent territory, else unclaimed, else center
    un_list = list(unclaimed)[:32]
    opp_list = list(oppT)[:32]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def man(a, b, x, y):
        return abs(a - x) + abs(b - y)

    # Precompute nearest distances from current position
    best_opp = min((man(sx, sy, x, y) for (x, y) in opp_list), default=None)
    best_un = min((man(sx, sy, x, y) for (x, y) in un_list), default=None)

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic: invalid move becomes stay

        # Determine move desirability
        score = 0
        if (nx, ny) in oppT:
            score += 200  # flipping into opponent territory is strong
        elif (nx, ny) in unclaimed:
            score += 80   # expanding into unclaimed is good

        # Frontier pressure: move toward nearest opp territory if available, else unclaimed
        if best_opp is not None:
            d = min((man(nx, ny, x, y) for (x, y) in opp_list), default=10**9)
            score += 40 - d
        if best_un is not None:
            d2 = min((man(nx, ny, x, y) for (x, y) in un_list), default=10**9)
            score += 12 - 0.6 * d2

        # Slight bias toward center to avoid drifting into dead ends
        score -= 0.05 * (abs(nx - cx) + abs(ny - cy))

        # Tie-break deterministically: prefer moves with larger dx then dy toward a fixed ordering
        tie = (dx, dy)
        if score > bestv or (score == bestv and tie < best[0:2]):
            bestv = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]