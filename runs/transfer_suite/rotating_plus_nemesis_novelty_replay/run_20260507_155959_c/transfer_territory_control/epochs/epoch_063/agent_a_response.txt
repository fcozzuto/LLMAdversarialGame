def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c is not None and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c is not None and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c is not None and len(c) >= 2)

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def adj_cells(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    frontier = set()
    if self_t:
        for x, y in self_t:
            for nx, ny in adj_cells(x, y):
                if (nx, ny) in unclaimed and free(nx, ny):
                    frontier.add((nx, ny))
    targets = list(frontier) if frontier else list(unclaimed)

    # If empty, drift toward center to avoid wasting moves.
    if not targets:
        tx, ty = w // 2, h // 2
    else:
        # Prefer closer targets, with slight preference to those nearer to opponent.
        # Deterministic tie-breakers.
        tx, ty = min(targets, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), - (abs(t[0] - ox) + abs(t[1] - oy)), t[0], t[1]))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        man = abs(nx - tx) + abs(ny - ty)
        score = -man
        if (nx, ny) in opp_t:
            score += 6  # immediate counterclaim
        if (nx, ny) in unclaimed:
            score += 2  # good for claiming
        if self_t and any((ax, ay) in self_t for ax, ay in adj_cells(nx, ny)):
            score += 1  # expand our territory boundary
        if (nx, ny) == (ox, oy):
            score += 1  # avoid giving up
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]