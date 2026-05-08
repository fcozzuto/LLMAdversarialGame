def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    selfset = set((int(p[0]), int(p[1])) for p in self_terr if p and len(p) >= 2)
    opposet = set((int(p[0]), int(p[1])) for p in opp_terr if p and len(p) >= 2)
    unq = [(int(p[0]), int(p[1])) for p in unclaimed if p and len(p) >= 2]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Direct pressure: if we can flip an opponent cell this turn, do it.
    best_flip = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs or not inb(nx, ny):
            continue
        if (nx, ny) in opposet:
            best_flip = [dx, dy]
            break
    if best_flip is not None:
        return best_flip

    # Build frontier targets: unclaimed adjacent to our territory (expand efficiently).
    frontier = []
    for (x, y) in unq:
        if (x, y) in selfset or (x, y) in opposet:
            continue
        for dx, dy in dirs:
            if (x + dx, y + dy) in selfset:
                frontier.append((x, y))
                break
    targets = frontier if frontier else unq

    if not targets:
        return [0, 0]

    # Deterministic scoring of immediate move based on target attraction and safety.
    def cell_score(nx, ny):
        if (nx, ny) in obs or not inb(nx, ny):
            return -10**9
        s = 0
        if (nx, ny) in selfset:
            s += 1
        elif (nx, ny) in opposet:
            s += 50  # shouldn't happen due to earlier flip check, but keep strong
        else:
            s += 30 if (nx, ny) in unq else 0

        # Encourage moving closer to nearest target.
        md = min(manh((nx, ny), t) for t in targets)
        s += -3 * md

        # Slightly prefer staying off obstacle-adjacent squares.
        adj_obs = 0
        for dx, dy in dirs:
            if inb(nx + dx, ny + dy) and (nx + dx, ny + dy) in obs:
                adj_obs += 1
        s += -2 * adj_obs
        return s

    best = [0, 0]
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        s = cell_score(nx, ny)
        if s > best_s:
            best_s = s
            best = [dx, dy]
    return best