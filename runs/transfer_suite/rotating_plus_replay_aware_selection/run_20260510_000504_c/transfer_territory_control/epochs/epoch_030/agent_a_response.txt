def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def neighbors8(x, y):
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    def is_blocked(x, y): return (x, y) in obstacles

    # Frontier candidates first
    frontier = set()
    if self_terr:
        for x, y in self_terr:
            for nx, ny in neighbors8(x, y):
                if (nx, ny) in unclaimed and not is_blocked(nx, ny):
                    frontier.add((nx, ny))

    # If we have no frontier, bias toward outer ring to counter center claim
    ring = []
    if not frontier:
        for x, y in unclaimed:
            if x == 0 or x == w - 1 or y == 0 or y == h - 1 or x == 1 or x == w - 2 or y == 1 or y == h - 2:
                ring.append((x, y))

    candidates = list(frontier) if frontier else (ring if ring else unclaimed)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_count = observation.get("opponent_territory_count", len(opp_terr))
    self_count = observation.get("self_territory_count", len(self_terr))
    defensive = opp_count >= self_count

    # Score each candidate deterministically
    best = None
    best_sc = None
    for tx, ty in candidates:
        if is_blocked(tx, ty):
            continue
        md = abs(tx - sx) + abs(ty - sy)
        center_pen = (abs(tx - cx) + abs(ty - cy))  # prefer farther from center
        edge_bonus = 0
        if tx in (0, w - 1) or ty in (0, h - 1) or tx in (1, w - 2) or ty in (1, h - 2):
            edge_bonus = 6
        opp_adj = 0
        for nx, ny in neighbors8(tx, ty):
            if (nx, ny) in opp_terr:
                opp_adj += 1
        # Attack when not defensive; otherwise protect by avoiding deep center pushes
        attack = -12 if defensive else 0
        sc = (-md) + edge_bonus + 0.6 * center_pen + (opp_adj * attack) + (0.01 * (tx * 8 + ty))
        if best is None or sc > best_sc:
            best = (tx, ty)
            best_sc = sc

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    # Ensure chosen step isn't blocked; if blocked, try alternative deterministic options
    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and not is_blocked(nx, ny):
        return [dx, dy]

    # Fallback: pick best among immediate moves by same scoring toward target
    bestm = [0, 0]
    bestv = None
    for mx, my in dirs:
        ax, ay = sx + mx, sy + my
        if not inb(ax, ay) or is_blocked(ax, ay):
            continue
        v = -(abs(tx - ax) + abs(ty - ay)) + 0.001 * (ax * 8 + ay)
        if bestv is None or v > bestv:
            bestv = v
            bestm = [mx, my]
    return bestm