def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (x, y))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((p[0], p[1]))

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if p is not None and len(p) >= 2:
            targets.append((p[0], p[1]))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()

    opp = (ox, oy)
    best_move = moves[0]
    best_score = -10**18

    if targets:
        # Score by closeness to nearest unclaimed, then distance from opponent
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = min(man((nx, ny), t) for t in targets)
            score = -d * 10 - man((nx, ny), opp)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # If no unclaimed info, chase nearest opponent territory (if provided), else hold
    oppT = observation.get("opponent_territory") or []
    tset = []
    for p in oppT:
        if p is not None and len(p) >= 2:
            tset.append((p[0], p[1]))

    if tset:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = min(man((nx, ny), t) for t in tset)
            score = -d * 10 + man((nx, ny), opp)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    return [0, 0]