def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                targets.append((x, y))
    if not targets:
        for p in observation.get("opponent_territory") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if valid(x, y):
                    targets.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if targets:
            d = min(man((nx, ny), t) for t in targets)
            # Prefer moves that reduce distance; deterministic tie-break by dir order
            score = d
        else:
            opp = observation.get("opponent_position") or (sx, sy)
            ox, oy = int(opp[0]), int(opp[1])
            score = man((nx, ny), (ox, oy))
        if score < best[0]:
            best = (score, [dx, dy])
    return best[1] if best[1] is not None else [0, 0]