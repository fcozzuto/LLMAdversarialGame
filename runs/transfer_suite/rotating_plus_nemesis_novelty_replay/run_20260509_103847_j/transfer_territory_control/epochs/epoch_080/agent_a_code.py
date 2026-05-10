def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))

    unT = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles and 0 <= x < w and 0 <= y < h:
                unT.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    neigh = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    def adj_count(cell, S):
        x, y = cell
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    best = None
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cell = (nx, ny)
        if cell in obstacles:
            continue
        score = 0
        if cell in unT:
            score += 120
        if cell in selfT:
            score += 35
        if cell in opT:
            score += 85  # flipping into opponent territory
        score += 6 * adj_count(cell, selfT)
        score -= 5 * adj_count(cell, opT)
        score += 2 * adj_count(cell, unT)
        # Prefer moving toward the nearer edge-unclaimed to counter edge claimers
        edge_un = 0
        if cell in unT and (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1):
            edge_un = 1
        score += 25 * edge_un
        # Deterministic tie-break: lower dx, then lower dy
        key = (score, -dx, -dy)
        if score > best_score or (score == best_score and key > best[0]):
            best_score = score
            best = (key, [dx, dy])
    return best[1] if best is not None else [0, 0]