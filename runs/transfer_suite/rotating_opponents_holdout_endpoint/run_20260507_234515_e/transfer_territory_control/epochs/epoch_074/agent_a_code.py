def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    target = None
    if unclaimed:
        target = min(unclaimed, key=lambda c: (man(sx, sy, c[0], c[1]), c[0], c[1]))
    else:
        if opp_terr:
            target = min(list(opp_terr), key=lambda c: (man(sx, sy, c[0], c[1]), c[0], c[1]))
        else:
            # fallback: head toward center
            target = (w // 2, h // 2)

    cx, cy = target
    best = None
    best_score = -10**18
    for dx, dy, nx, ny in valid:
        score = 0
        d = man(nx, ny, cx, cy)
        score -= 2.0 * d

        if (nx, ny) in opp_terr:
            score += 8.0  # immediate capture
        if (nx, ny) in self_terr:
            score += 1.0  # safe expansion
        if (nx, ny) in unclaimed:
            score += 2.5  # claim new territory

        # Prefer moves that reduce distance to opponent/target while not drifting away too much
        score -= 0.05 * (man(nx, ny, w // 2, h // 2))

        # Deterministic tie-break
        key = (score, -abs(dx), -abs(dy), nx, ny)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]