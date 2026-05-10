def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(x), int(y)) for x, y in unclaimed if x is not None and y is not None)

    their_terr = observation.get("opponent_territory") or []
    their_set = set((int(x), int(y)) for x, y in their_terr if x is not None and y is not None)

    adj_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    targets = []
    for x, y in their_set:
        for dx, dy in adj_dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in un_set:
                targets.append((nx, ny))
    if not targets:
        targets = list(un_set)

    if not targets:
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in dirs:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    tx, ty = min(targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    if not inb(sx + dx, sy + dy):
        candidates = []
        for adx, ady in adj_dirs:
            if inb(sx + adx, sy + ady):
                candidates.append((abs(tx - (sx + adx)) + abs(ty - (sy + ady)), adx, ady))
        if candidates:
            _, adx, ady = min(candidates)
            return [adx, ady]
        return [0, 0]

    return [dx, dy]