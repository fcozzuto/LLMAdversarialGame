def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    self_terr = observation.get("self_territory", []) or []
    opp_terr = observation.get("opponent_territory", []) or []
    self_set = {(p[0], p[1]) for p in self_terr if inb(p[0], p[1])}
    opp_set = {(p[0], p[1]) for p in opp_terr if inb(p[0], p[1])}
    unclaimed = [(p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []) if len(p) >= 2 and inb(p[0], p[1]) and (p[0], p[1]) not in obstacles]
    if not unclaimed:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    center = (w - 1) / 2.0, (h - 1) / 2.0

    unclaimed_set = set(unclaimed)
    frontier = set()
    for x, y in self_set:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed_set:
                frontier.add((nx, ny))
    candidates = list(frontier) if frontier else unclaimed

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    bestv = None
    for tx, ty in candidates:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # maximize: being closer than opponent + slight center bias
        cb = -abs(tx - center[0]) - abs(ty - center[1])
        v = (do - ds) * 1000 - ds * 2 + cb
        if best is None or v > bestv or (v == bestv and (tx, ty) < best):
            best = (tx, ty)
            bestv = v

    tx, ty = best
    # choose best immediate step toward best target while avoiding obstacles
    best_step = (0, 0)
    best_step_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # prefer moves that reduce distance to target; break ties by minimizing opponent distance
        ns = man(nx, ny, tx, ty)
        no = man(nx, ny, ox, oy)
        score = (-ns) * 1000 - no
        if best_step_score is None or score > best_step_score or (score == best_step_score and (dx, dy) < best_step):
            best_step_score = score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]