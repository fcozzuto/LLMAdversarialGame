def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    neigh8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    dirs = [(-1,0),(0,-1),(1,0),(0,1),(-1,-1),(1,-1),(-1,1),(1,1),(0,0)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    frontier = set()
    if self_terr:
        for x, y in unclaimed:
            for dx, dy in neigh8:
                if (x+dx, y+dy) in self_terr:
                    frontier.add((x, y))
                    break

    if frontier:
        target = min(frontier, key=lambda c: (manh((sx, sy), c), c[0], c[1]))
        prefer = 1
    elif unclaimed:
        target = min(unclaimed, key=lambda c: (manh((sx, sy), c), c[0], c[1]))
        prefer = 1
    elif opp_terr:
        target = min(opp_terr, key=lambda c: (manh((sx, sy), c), c[0], c[1]))
        prefer = 0
    else:
        target = (w // 2, h // 2)
        prefer = 0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nt = (nx, ny)
        d = manh(nt, target)
        cell = 1 if nt in unclaimed else (2 if nt in opp_terr else (0 if nt in self_terr else 3))
        # Prefer unclaimed expansion; allow invasion when no unclaimed.
        bonus = 0
        if prefer == 1:
            if cell == 1: bonus += 20
            elif cell == 2: bonus -= 5
        else:
            if cell == 2: bonus += 15
            elif cell == 1: bonus += 8
        # Small tie-breaker to avoid oscillations: favor consistent direction by projecting toward target.
        proj = (0 if target[0] == sx else (1 if target[0] > sx else -1)) * dx + (0 if target[1] == sy else (1 if target[1] > sy else -1)) * dy
        score = -d + bonus + 0.001 * proj - 0.0001 * (nx * 10 + ny)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]