def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            oppT.add((x, y))

    unclaimed = []
    unch = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                unclaimed.append((x, y))
                unch.add((x, y))

    if not unclaimed and not oppT:
        return [0, 0]

    neigh8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    frontier = []
    if unclaimed and oppT:
        for (x, y) in unclaimed:
            for dx0, dy0 in neigh8:
                if (x + dx0, y + dy0) in oppT:
                    frontier.append((x, y))
                    break

    def dist(a, b):
        ax, ay = a
        bx, by = b
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    targets = frontier if frontier else unclaimed
    move_options = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in move_options:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        npos = (nx, ny)

        score = 0
        if npos in oppT:
            score += 500  # immediate steal
        if npos in unch:
            score += 20
        score -= dist(npos, (ox, oy)) * 0.5  # keep pressure near opponent

        if targets:
            tx, ty = min(targets, key=lambda t: dist(npos, t))
            score += (300 - dist(npos, (tx, ty)) * 2)
            if frontier and npos in unch:
                score += 30 if any((nx + a, ny + b) in oppT for a, b in neigh8) else 0

        # deterministic tie-break: prefer lexicographically smaller (dx,dy)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]