def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

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

    opp_terr = observation.get("opponent_territory") or []
    opp_set = set((p[0], p[1]) for p in opp_terr if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    candidates = []
    if opp_set:
        for x, y in unclaimed:
            for nx, ny in neighbors8(x, y):
                if (nx, ny) in opp_set:
                    candidates.append((x, y))
                    break
    targets = candidates if candidates else unclaimed

    if not targets:
        return [0, 0]

    cx, cy = w // 2, h // 2
    # Prefer cells near the opponent's center-claim and on the "boundary" of opponent territory.
    best = None
    best_key = None
    for x, y in targets:
        key = (man(x, y, ox, oy), -man(x, y, cx, cy), man(x, y, sx, sy))
        if best is None or key < best_key:
            best, best_key = (x, y), key
    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    # If all moves blocked, allow staying.
    if not moves:
        return [0, 0]

    stay_dist = man(sx, sy, tx, ty)
    best_move = None
    best_val = None
    # Deterministic tie-break: sorted by (dist, -progress, dx, dy)
    for dx, dy, nx, ny in moves:
        dist = man(nx, ny, tx, ty)
        progress = stay_dist - dist
        opp_dist = man(nx, ny, ox, oy)
        val = (dist, -progress, opp_dist, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]