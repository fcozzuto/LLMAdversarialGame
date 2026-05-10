def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    opp_frontier = []
    for ox, oy in oppT:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = ox + dx, oy + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    if (nx, ny) in unclaimed:
                        opp_frontier.append((nx, ny))
    if opp_frontier:
        goal = min(opp_frontier, key=lambda c: dist2((sx, sy), c))
    else:
        candidates = []
        for x, y in unclaimed:
            if x in (0, w - 1) or y in (0, h - 1):
                if (x, y) not in obstacles:
                    candidates.append((x, y))
        goal = min(candidates, key=lambda c: dist2((sx, sy), c)) if candidates else None

    best = (0, (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        score = 0
        if (nx, ny) in unclaimed:
            score += 3
        if (nx, ny) in oppT:
            score += 6  # flipping on entry is enabled
        if (nx, ny) in selfT:
            score += 0

        if goal is not None:
            score += 4 - (dist2((nx, ny), goal) // 4)

        # Prefer not to move away from opponent when no good unclaimed targets exist
        if not opp_frontier and oppT:
            nearest_opp = min(oppT, key=lambda c: dist2((nx, ny), c))
            score += (dist2((sx, sy), nearest_opp) - dist2((nx, ny), nearest_opp)) // 2

        # Tie-break deterministically by move ordering (dirs list order)
        if score > best[0]:
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]