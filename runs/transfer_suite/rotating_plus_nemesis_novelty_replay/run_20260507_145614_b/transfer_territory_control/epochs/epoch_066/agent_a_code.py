def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_set = set((p[0], p[1]) for p in self_terr if p and len(p) >= 2)
    opp_set = set((p[0], p[1]) for p in opp_terr if p and len(p) >= 2)

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**9
    if not unclaimed:
        return [0, 0]

    # deterministic tie-break by (score, x, y)
    for x, y in unclaimed:
        adj_opp = 0
        adj_self = 0
        edge = 1 if (x == 0 or x == w - 1 or y == 0 or y == h - 1) else 0
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in opp_set:
                adj_opp = 1
            if (nx, ny) in self_set:
                adj_self = 1
        # Prefer denying near opponent; otherwise expand from our frontier; prefer edge slightly.
        score = (50 if adj_opp else 0) + (10 if adj_self else 0) + (6 if edge else 0) - 0.8 * man(sx, sy, x, y)
        if score > best_score or (score == best_score and (x < best[0] if best else True)):
            best_score = score
            best = (x, y)

    tx, ty = best
    if tx == sx and ty == sy:
        return [0, 0]

    # choose the next step that reduces distance to the target while not stepping into obstacles
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((man(nx, ny, tx, ty), nx, ny, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    return [candidates[0][3], candidates[0][4]]