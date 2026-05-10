def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def manh(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    if not self_terr:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        if inb(sx + dx, sy + dy): return [dx, dy]
        return [0, 0]

    frontier = []
    for (x, y) in self_terr:
        for dx, dy in moves:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed and inb(nx, ny):
                frontier.append((nx, ny))
    targets = frontier if frontier else list(unclaimed)

    if targets:
        tx, ty = min(targets, key=lambda p: (manh(p[0], p[1], sx, sy), p[0], p[1]))
    else:
        tx, ty = (ox, oy)  # nowhere to expand: contest

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        score = 0
        if (nx, ny) in self_terr:
            score -= 2
        elif (nx, ny) in unclaimed:
            score += 10
        elif (nx, ny) in opp_terr:
            score += 14
        else:
            score -= 1
        # prefer reducing distance to target, and slightly avoid stepping near opponent if not contesting
        score += -manh(nx, ny, tx, ty)
        if (nx, ny) not in opp_terr:
            score += -0.2 * manh(nx, ny, ox, oy)
        # deterministic tie-breaker
        tup = (score, -abs(dx), -abs(dy), dx, dy)
        if best is None or tup > best[0]:
            best = (tup, dx, dy)

    return [int(best[1]), int(best[2])] if best is not None else [0, 0]