def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal_moves.append((dx, dy, nx, ny))

    if not legal_moves:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Prefer resources where we are closer than the opponent; otherwise, pick the one with least disadvantage.
    best = None
    best_score = 10**18
    for rx, ry in resources:
        if (rx, ry) in obst:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Strongly favor being ahead, also account for absolute distance (we need to finish).
        ahead_bonus = 0
        if ds < do:
            ahead_bonus = (do - ds) * 2000 + 500
        # If both are tied, slightly prefer the resource closer to us.
        tie_bonus = 0
        if ds == do:
            tie_bonus = -5
        # Mildly penalize resources near the opponent (to avoid "race" picking).
        opp_pressure = cheb(ox, oy, rx, ry) * 2
        score = (ds - do) * 1000 + ds - ahead_bonus - tie_bonus + opp_pressure
        if score < best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best
    # Greedy step towards target, but avoid stepping into obstacles.
    best_step = [0, 0]
    best_dist = 10**18
    best_tiebreak = 10**18
    for dx, dy, nx, ny in legal_moves:
        d = cheb(nx, ny, tx, ty)
        # Tie-break: prefer steps that also reduce ds compared to opponent reaching.
        step_score2 = (d - cheb(nx, ny, tx, ty))  # always 0; keep deterministic structure
        if d < best_dist:
            best_dist = d
            best_step = [dx, dy]
            best_tiebreak = step_score2
        elif d == best_dist:
            if step_score2 < best_tiebreak:
                best_step = [dx, dy]
                best_tiebreak = step_score2
    return best_step