def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Targets: unclaimed cells first, else opponent territory, else approach opponent.
    if unclaimed:
        targets = list(unclaimed)
    elif opp_terr:
        targets = list(opp_terr)
    else:
        targets = [(ox, oy)]

    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        score = 0

        # Territory value
        if cell in opp_terr:
            score += 7
        elif cell in unclaimed:
            score += 5
        elif cell in self_terr:
            score += 1

        # Edge expansion bonus (often creates lengthier fronts)
        if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
            score += 2

        # Approach the nearest valuable target
        nt = min(targets, key=lambda p: dist(nx, ny, p[0], p[1]))
        score -= 0.6 * dist(nx, ny, nt[0], nt[1])

        # Also prefer moves that reduce distance to opponent when we can capture
        if opp_terr or unclaimed:
            score += 0.2 * (dist(sx, sy, ox, oy) - dist(nx, ny, ox, oy))

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]