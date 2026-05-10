def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def n8(x, y):
        res = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny):
                        res.append((nx, ny))
        return res

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    frontier = []
    for uc in unclaimed:
        if any(p in opp_t for p in n8(uc[0], uc[1])):
            frontier.append(uc)
    targets = frontier if frontier else (list(unclaimed) if unclaimed else [])

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        score = 0
        if (nx, ny) in opp_t:
            score += 30
        elif (nx, ny) in unclaimed:
            score += 8
        elif (nx, ny) in self_t:
            score += 2
        else:
            score += 0

        if targets:
            nearest = min(targets, key=lambda t: dist2((nx, ny), t))
            score += -0.02 * dist2((nx, ny), nearest)
        score += 0.005 * (-(dist2((nx, ny), (ox, oy))))  # slightly prefer being closer to opponent
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]