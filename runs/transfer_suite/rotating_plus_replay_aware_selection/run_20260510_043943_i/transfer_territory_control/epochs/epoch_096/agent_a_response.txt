def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_t = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    frontier = set()
    for x, y in self_t:
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed or (nx, ny) in opp_t:
                    frontier.add((nx, ny))

    if not frontier:
        frontier = set(unclaimed) if unclaimed else set(opp_t)

    def dist_to_set(x, y, S):
        if not S:
            return 10**9
        return min(abs(x - a) + abs(y - b) for a, b in S)

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            cand.append((nx, ny, dx, dy))

    if not cand:
        return [0, 0]

    best = None
    for nx, ny, dx, dy in cand:
        score = 0.0
        if (nx, ny) in opp_t:
            score += 40.0
        if (nx, ny) in unclaimed:
            score += 18.0
        if (nx, ny) in self_t:
            score -= 2.0

        # Reward taking/approaching frontier and capturing adjacent cells
        for ax, ay in neigh:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                if (tx, ty) in opp_t:
                    score += 8.0
                elif (tx, ty) in unclaimed:
                    score += 4.0

        score += 6.0 / (1.0 + dist_to_set(nx, ny, frontier))
        # Slightly prefer moves that progress toward global frontier if stuck
        score -= 0.15 * dist_to_set(nx, ny, unclaimed if unclaimed else opp_t)

        # Deterministic tie-break: prefer larger dx then larger dy then stay
        tie = (score, dx, dy)
        if best is None or tie > best[0]:
            best = (tie, [dx, dy])

    return best[1]