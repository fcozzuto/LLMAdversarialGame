def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(xy) for xy in (observation.get("unclaimed_cells", []) or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    opp_center = (ox, oy)
    if opp_cells:
        sx2 = sy2 = 0
        n = len(opp_cells)
        for x, y in opp_cells:
            sx2 += x
            sy2 += y
        opp_center = (sx2 // n, sy2 // n)
    cx, cy = w // 2, h // 2

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_cells:
            base = 120
        elif (nx, ny) in unclaimed:
            base = 35
        elif (nx, ny) in self_cells:
            base = 8
        else:
            base = 12
        # bias toward center and toward pressuring opponent
        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - opp_center[0]) + abs(ny - opp_center[1])
        # deterministically break ties: prefer diagonal then cardinal then stay
        diag = 1 if dx != 0 and dy != 0 else 0
        card = 1 if (dx == 0) ^ (dy == 0) else 0
        stay = 1 if (dx == 0 and dy == 0) else 0
        score = base + (18 - d_center) + (8 - d_opp // 2) + diag * 0.3 + card * 0.1 - stay * 0.5
        cand.append((score, -diag, -card, stay, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [cand[0][4], cand[0][5]]