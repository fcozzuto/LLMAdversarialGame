def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        # deterministic "predator intercept": move to reduce distance to opponent
        return [-sign(ox - x), -sign(oy - y)]

    # Pick the best immediate move by scoring the position after the move against all resources.
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or cell_blocked(nx, ny):
            continue

        # Evaluate: prefer resources we can beat opponent to, and closer ones overall.
        # Small penalties for moves that increase distance to opponent (keeps us pressure-ready).
        best_for_move = None
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # advantage: positive if we are closer (using current opponent pos as baseline)
            adv = opd - myd
            # tie-breakers: closer to resource, and if near, maximize margin; slight preference to nearer to opponent
            key = (adv, -myd, -man(nx, ny, ox, oy))
            if best_for_move is None or key > best_for_move:
                best_for_move = key

        # If a move can't score (shouldn't happen), ignore it.
        if best_for_move is None:
            continue

        # Additional shaping: prefer staying away from obstacles adjacency-less; deterministic but light.
        base_adv, neg_myd, neg_opp = best_for_move
        score = (base_adv, neg_myd, neg_opp)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]