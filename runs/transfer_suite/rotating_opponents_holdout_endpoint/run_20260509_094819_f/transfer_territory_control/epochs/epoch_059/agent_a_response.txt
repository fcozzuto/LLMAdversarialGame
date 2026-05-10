def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in (observation.get("self_territory") or []):
        if p is not None and len(p) == 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in (observation.get("opponent_territory") or []):
        if p is not None and len(p) == 2:
            opp_t.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p is not None and len(p) == 2:
            unclaimed.append((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target selection: prefer nearest unclaimed, else nearest opponent territory (to counterclaim)
    if unclaimed:
        target = sorted(unclaimed, key=lambda t: (man((sx, sy), t), t[0], t[1]))[0]
    elif opp_t:
        target = sorted(list(opp_t), key=lambda t: (man((sx, sy), t), t[0], t[1]))[0]
    else:
        return [0, 0]

    best = (10**9, 10**9)
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Minimize distance to target; slight preference for entering unclaimed/self for continuity
        d = abs(nx - target[0]) + abs(ny - target[1])
        in_self = 1 if (nx, ny) in self_t else 0
        in_opp = 1 if (nx, ny) in opp_t else 0
        # If entering opponent territory, allow it but don't chase unless it's closest.
        # This keeps deterministic, simple behavior that still counters.
        tie = (0 - in_opp, -in_self)  # prefers self over opp when distances equal
        score = (d, tie[0] + tie[1] * 0)
        if score < best:
            best = score
            best_move = [dx, dy]
    return best_move