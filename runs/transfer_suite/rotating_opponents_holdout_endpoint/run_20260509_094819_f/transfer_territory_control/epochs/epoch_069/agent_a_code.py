def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []) if x is not None)
    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    # Focus: squares adjacent to opponent territory but not already ours.
    opp_front = set()
    for x, y in opp_t:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in self_t:
                opp_front.add((nx, ny))

    targets = []
    for c in opp_front:
        if c in unclaimed or c in opp_t:
            targets.append(c)
    if not targets:
        # Secondary: grab nearest unclaimed cell not blocked.
        targets = [c for c in unclaimed if c not in obstacles]
    if not targets:
        # Last resort: go toward opponent to contest.
        targets = [(ox, oy)]

    best = None
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Score for this landing cell.
        score = 0
        if (nx, ny) in unclaimed: score += 6
        if (nx, ny) in opp_t: score += 7  # flipping on entry
        if (nx, ny) in opp_front: score += 5
        if (nx, ny) in self_t: score -= 2  # prefer expansion
        # Move/target shaping: reduce distance to nearest target, but prefer staying near opponent front.
        dmin = 10**9
        for tx, ty in targets[:12]:  # deterministic cap
            d = abs(tx - nx) + abs(ty - ny)
            if d < dmin: dmin = d
        score -= dmin
        # Slight bias toward opponent's position to prevent stagnation.
        score -= 0.05 * (abs(ox - nx) + abs(oy - ny))
        # Deterministic tie-break: prefer lexicographically smaller (dx,dy) for stable behavior.
        if score > best_score or (score == best_score and (best is None or (dx, dy) < best)):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]