def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_opp = (nx, ny) in oppT
        is_uncl = (nx, ny) in unclaimed
        is_self = (nx, ny) in selfT

        # Base: head toward center while not giving opponent nearby targets.
        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)

        score = 0.0
        score += (2000.0 if is_opp else 0.0)          # flip/capture opponent
        score += (120.0 if is_uncl else 0.0)         # expand into unclaimed
        score += (10.0 if is_self else 0.0)          # stable moves
        score += -1.5 * d_center                       # prefer center
        score += -0.8 * d_opp if is_opp else 0.4 * d_opp  # if capturing, be closer; else keep distance

        # Small preference for not standing still once we have options
        if dx == 0 and dy == 0 and (is_uncl or is_opp):
            score -= 5.0

        # Deterministic tie-break: lower dx,dy order as listed
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]