def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    turn = int(observation.get("turn_index", 0) or 0)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Choose resource where we have the most "reach advantage" over opponent.
    remain = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    phase = (turn + remain) % 4  # deterministic mode switch
    best = None
    best_val = None
    for x, y in resources:
        ds = dist(sx, sy, x, y)
        do = dist(ox, oy, x, y)
        adv = do - ds  # positive means we can reach earlier (or equal)
        # Bias: early game be more aggressive, late game prefer safety/close-by.
        if phase in (0, 1):
            val = adv * 10 - ds
        elif phase == 2:
            val = adv * 12 - (ds + do) * 0.2
        else:
            val = adv * 8 - ds * 1.2
        if best_val is None or (val > best_val) or (val == best_val and (x, y) < best):
            best_val = val
            best = (x, y)

    tx, ty = best

    # Greedy one-step evaluation, avoid obstacles, and keep some separation from opponent.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    def lex_key(dx, dy):  # deterministic tie-breaker
        return (abs(dx) + abs(dy), dx, dy)

    bestm = None
    bestscore = None
    for dx, dy, nx, ny in moves:
        ds2 = dist(nx, ny, tx, ty)
        do2 = dist(nx, ny, ox, oy)
        # Score: move toward target strongly; if contest likely, prefer moving away from opponent.
        # Also small preference to reduce ds2 vs staying.
        score = -ds2 * 3.0
        # Opponent influence: when opponent is close to us, keep distance.
        score += (do2) * (0.15 + 0.05 * (phase == 2))
        # If opponent is also targeting region, slightly discourage getting too close to them while chasing.
        score += dist(ox, oy, tx, ty) * (-0.02 if phase == 1 else -0.01)

        if bestscore is None or score > bestscore or (score == bestscore and lex_key(dx, dy) < lex_key(bestm[0], bestm[1])):
            bestscore = score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]