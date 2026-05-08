def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    px, py = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    selfT = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            selfT.add((p[0], p[1]))

    oppT = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            oppT.add((p[0], p[1]))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Frontier target: prefer cells adjacent to our territory that are not ours (unclaimed or opponent).
    frontier = set()
    for (x, y) in selfT:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in selfT and (nx, ny) not in obstacles:
                    frontier.add((nx, ny))

    # If no frontier yet, fall back to global unclaimed, else opponent territory.
    fallback = None
    if frontier:
        fallback = min(frontier, key=lambda t: (man(sx, sy, t[0], t[1]), man(px, py, t[0], t[1]), t[0], t[1]))
    else:
        candidates = list(unclaimed) if unclaimed else list(oppT)
        if candidates:
            fallback = min(candidates, key=lambda t: (man(sx, sy, t[0], t[1]), man(px, py, t[0], t[1]), t[0], t[1]))

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep in place
            dx, dy = 0, 0

        score = 0
        if (nx, ny) in selfT:
            score += 2
        if (nx, ny) in oppT:
            score += 10  # flipping on entry
        if (nx, ny) in unclaimed:
            score += 7

        # Move toward the chosen frontier/global target.
        if fallback is not None:
            score += (20 - 2 * man(nx, ny, fallback[0], fallback[1]))

        # Control pressure: prefer being closer to opponent position too.
        score += max(0, 8 - man(nx, ny, px, py))

        # Slight deterministic tie-break by ordering of deltas.
        key = (-(score), dx, dy, nx, ny)
        if best_score is None or key < best_score:
            best_score = key
            best_move = [dx, dy]

    return best_move