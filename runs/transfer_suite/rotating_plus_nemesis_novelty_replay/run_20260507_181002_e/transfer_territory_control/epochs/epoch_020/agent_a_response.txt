def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    if not unclaimed:
        unclaimed = set(resources)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs_center = [(1, 1), (1, 0), (0, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1), (0, 0)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    candidates = []
    for dx, dy in dirs_center:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0.0
        if (nx, ny) in oppT:
            score += 1000.0  # strong counterclaim swing
        elif (nx, ny) in unclaimed or (nx, ny) in resources:
            score += 300.0  # secure expansion
        elif (nx, ny) in selfT:
            score += 40.0   # consolidate
        else:
            score += 5.0    # allow progress toward frontier

        # Drive toward opponent when we have a nearby frontier target
        d_opp = abs(nx - ox) + abs(ny - oy)
        score += (60.0 - d_opp) * 2.0

        # Also pull toward nearest opponent territory cell if it exists
        if oppT:
            best_opp = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in oppT)
            score += (90.0 - best_opp) * 1.5

        # Light pull toward center to avoid corner stagnation against counterclaimers
        score += -(abs(nx - cx) + abs(ny - cy)) * 0.8

        # If very close to border of opp territory, prefer staying on that contact line
        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]