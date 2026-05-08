def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_terr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    frontier = set()
    for (x, y) in opp_terr:
        for nx, ny in neighbors(x, y):
            if (nx, ny) not in obstacles and ((nx, ny) in unclaimed):
                frontier.add((nx, ny))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    def dist_to_frontier(x, y):
        if not frontier:
            return abs(x - (w - 1)) + abs(y - (h - 1))
        d = 10**9
        for fx, fy in frontier:
            dd = abs(x - fx) + abs(y - fy)
            if dd < d:
                d = dd
        return d

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in opp_terr:
            score += 12  # flipping opponent territory is strong
        if (nx, ny) in unclaimed:
            score += 6   # expand into neutral
        if (nx, ny) in self_terr:
            score -= 1   # avoid wasting moves unless needed

        # Approach opponent frontier when possible
        df = dist_to_frontier(nx, ny)
        score += max(0, 8 - df * 0.7)

        # Mild tie-break: prefer moves that don't increase distance from opponent
        ox, oy = observation.get("opponent_position", (w - 1, h - 1))
        ox, oy = int(ox), int(oy)
        score -= (abs(nx - ox) + abs(ny - oy)) * 0.05

        if score > best_score or (score == best_score and [dx, dy] < best_move):
            best_score = score
            best_move = [dx, dy]

    return best_move