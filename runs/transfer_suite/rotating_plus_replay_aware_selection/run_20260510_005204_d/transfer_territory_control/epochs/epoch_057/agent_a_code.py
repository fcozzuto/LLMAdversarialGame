def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(x1, y1, x2, y2):
        ax = x1 - x2; ay = y1 - y2
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    # Build frontier of our territory: unclaimed cells adjacent to our territory
    frontier = set()
    for (x, y) in self_terr:
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed and inb(nx, ny):
                frontier.add((nx, ny))

    # Deterministic target preference order: prefer frontier, else unclaimed, else any in-bounds move
    targets = list(frontier) if frontier else list(unclaimed)
    if not targets:
        targets = [(x, y) for x in range(max(0, sx - 1), min(w, sx + 2)) for y in range(max(0, sy - 1), min(h, sy + 2)) if inb(x, y)]

    # Choose move by local heuristic on resulting cell
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep us; mimic deterministically

        score = 0
        # Capture value
        if (nx, ny) in opp_terr:
            score += 8
        elif (nx, ny) in self_terr:
            score += 2

        # Frontier / unclaimed expansion
        if (nx, ny) in unclaimed:
            score += 6
        if (nx, ny) in frontier:
            score += 10

        # Progress toward nearest preferred target (and slightly away from opponent)
        tx = targets[0][0]; ty = targets[0][1]
        min_dt = 10**9
        for (tqx, tqy) in targets:
            dt = d(nx, ny, tqx, tqy)
            if dt < min_dt:
                min_dt = dt; tx, ty = tqx, tqy
        score += 5 / (1 + min_dt)  # deterministic float-free would be better; but safe and deterministic
        score += -0.06 * d(nx, ny, ox, oy)

        # Tie-break: prefer staying if equal, else deterministic by move order (already fixed)
        if score > best_score:
            best_score = score; best = (dx, dy)

    return [int(best[0]), int(best[1])]