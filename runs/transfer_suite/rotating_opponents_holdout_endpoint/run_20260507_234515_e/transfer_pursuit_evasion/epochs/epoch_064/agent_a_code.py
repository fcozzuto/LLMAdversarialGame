def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                oset.add((int(p[0]), int(p[1])))
            except:
                pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in oset:
                candidates.append((dx, dy))

    self_role = str(observation.get("self_role", ""))
    pursuer = ("pursuer" in self_role.lower()) or ("pursuit" in self_role.lower())
    if not pursuer:
        pursuer = str(observation.get("opponent_role", "")).lower().find("purs") != -1

    toward = (0 if ox == sx else (1 if ox > sx else -1), 0 if oy == sy else (1 if oy > sy else -1))
    opposite = (-toward[0], -toward[1])

    if pursuer:
        best = None
        bestd = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            d = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            if best is None or d < bestd or (d == bestd and (dx, dy) == toward):
                best, bestd = (dx, dy), d
        return [int(best[0]), int(best[1])]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Deterministic: pick farthest corner from opponent; break ties toward opposite direction.
    target = corners[0]
    bestcorner_score = -1
    for c in corners:
        cx, cy = c
        d = (cx - ox) * (cx - ox) + (cy - oy) * (cy - oy)
        if d > bestcorner_score:
            bestcorner_score = d
            target = c

    tx, ty = target
    tdx = 0 if tx == sx else (1 if tx > sx else -1)
    tdy = 0 if ty == sy else (1 if ty > sy else -1)

    best = None
    bestd = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d_away = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        align = -((tx - nx) * (tx - nx) + (ty - ny) * (ty - ny))
        score = d_away * 1000000 + align
        if best is None or score > bestd or (score == bestd and (dx, dy) == (tdx, tdy)):
            best, bestd = (dx, dy), score
    return [int(best[0]), int(best[1])]