def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    # Pick best target resource by advantage (my closer than opponent)
    best_target = resources[0]
    best_adv = -10**9
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # positive means I can get there sooner
        # Slight preference to nearer resources when tied
        if adv > best_adv or (adv == best_adv and myd < cheb(sx, sy, best_target[0], best_target[1])):
            best_adv = adv
            best_target = [rx, ry]
    tx, ty = best_target

    # If I'm not ahead, try to move to reduce opponent's progress (resource denier)
    # by favoring moves that reduce opponent distance to the same target least, and my distance most.
    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    # Deterministic tie-break: fixed move order, score then distance then lex.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        # Core: minimize my distance to target
        score = -myd2 * 10.0
        # Advantage shaping: reward increasing my lead vs opponent at the target
        score += (opd2 - myd2) * 2.5

        # If opponent can beat me (my not ahead), add denial: avoid moves that bring me closer
        # while I can't win pickup race; instead, try to drift toward a better side of the map.
        if best_adv <= 0:
            score -= myd2 * 0.8
            # Prefer increasing distance to opponent a bit (survival/denial positioning)
            oppd = cheb(nx, ny, ox, oy)
            score += oppd * 0.1

        # Obstacle avoidance already handled; small penalty for moving away from target
        if (abs(nx - tx) + abs(ny - ty)) > (abs(sx - tx) + abs(sy - ty)):
            score -= 0.3

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all moves were invalid (shouldn't happen), stay still.
    if best_move is None:
        return [0, 0]
    return best_move