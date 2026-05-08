def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))
    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))
    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors_of(tset):
        nb = set()
        for x, y in tset:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    nb.add((nx, ny))
        return nb

    opp_front = neighbors_of(oppT)
    # If opponent has no territory yet, bias to center and our expansion.
    if not opp_front:
        opp_front = set([(cx, cy)])

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    # Tie-breaker order: closer to center, then prefer diagonals toward targets, then deterministic.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        score = 0
        if (nx, ny) in oppT:
            score += 14
        elif (nx, ny) in unclaimed:
            score += 9
        elif (nx, ny) in selfT:
            score += 2
        else:
            score += 1

        # Push toward opponent front to maximize flips/claims.
        score += 6 * (1 if (nx, ny) in opp_front else 0)
        d_front = min((man(nx, ny, fx, fy) for fx, fy in opp_front), default=0)
        score -= d_front

        # Also keep pressure toward center so we don't get cornered by leader bonus.
        score -= 0.35 * man(nx, ny, cx, cy)

        # Deterministic key: higher score, then prefer lexicographically smaller move.
        key = (-score, dx, dy, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best