def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    myT = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            myT.add((int(p[0]), int(p[1])))
    oppT = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    nbrs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not inb(sx, sy):
        for dx, dy in nbrs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    frontier = []
    if myT:
        for (x, y) in myT:
            for dx, dy in nbrs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in myT:
                    frontier.append((nx, ny))

    unclaimed_set = set(unclaimed)
    candidate_targets = []
    if frontier:
        for t in frontier:
            if t in unclaimed_set or t in oppT or True:
                candidate_targets.append(t)
    if not candidate_targets:
        candidate_targets = unclaimed[:] if unclaimed else [(ox, oy)]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in nbrs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer: expanding into unclaimed, reaching near opponent/control, and staying near our territory.
        score = 0
        if (nx, ny) in oppT:
            score += 40  # likely immediate flip
        if (nx, ny) in unclaimed_set:
            score += 30
        score -= md(nx, ny, ox, oy) * 2  # pressure opponent
        if myT:
            score -= min(md(nx, ny, tx, ty) for (tx, ty) in myT) * 0.6
        # If there are unclaimed, bias toward closest unclaimed to this neighbor.
        if unclaimed:
            score += 16 - min(md(nx, ny, tx, ty) for (tx, ty) in unclaimed) * 1.2
        # Mild preference to avoid getting stuck on edges far from progress
        score += 0.1 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * -1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]