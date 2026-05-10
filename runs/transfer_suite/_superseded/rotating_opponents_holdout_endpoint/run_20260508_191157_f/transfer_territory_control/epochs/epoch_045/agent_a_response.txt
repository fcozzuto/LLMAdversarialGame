def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = set(map(tuple, observation.get("resources") or []))

    # Candidate move scoring (1-step lookahead)
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        cell = (nx, ny)
        d_to_opp = max(abs(nx - ox) + abs(ny - oy), 0)
        # Encourage pushing toward opponent and flipping/capturing.
        score = 0
        if cell in opp_t:
            score += 200
        elif cell in unclaimed:
            score += 70
        elif cell in resources:
            score += 50
        elif cell in self_t:
            score += 10
        # Slightly prefer closer to opponent to keep pressure.
        score += 6 * (14 - d_to_opp)
        # If we can immediately approach a frontier, boost.
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                nn = (nx + ax, ny + ay)
                if nn in opp_t:
                    score += 25
        scored.append((score, -abs(nx - ox) - abs(ny - oy), dx, dy))

    if not scored:
        return [0, 0]
    scored.sort(reverse=True)
    best_score, _, dx, dy = scored[0]

    # If we are adjacent to an opponent-owned cell, prioritize flipping deterministically.
    for dx2, dy2 in moves:
        nx, ny = sx + dx2, sy + dy2
        if in_bounds(nx, ny) and (nx, ny) in opp_t:
            return [dx2, dy2]

    return [int(dx), int(dy)]