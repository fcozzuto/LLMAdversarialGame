def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    legal = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        best = None
        bestv = 10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, ox, oy)
            if d < bestv:
                bestv = d
                best = (dx, dy)
        return [best[0], best[1]]

    # pick target resource where we can most improve relative position vs opponent
    best_target = None
    best_adv = -10**18
    for tx, ty in resources:
        myd = man(sx, sy, tx, ty)
        opd = man(ox, oy, tx, ty)
        adv = opd - myd
        if adv > best_adv or (adv == best_adv and (myd < man(sx, sy, best_target[0], best_target[1]) if best_target else True)):
            best_adv = adv
            best_target = (tx, ty)

    tx, ty = best_target
    # choose move that maximizes immediate advantage to that target; slight tiebreak toward survival/spacing
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd2 = man(nx, ny, tx, ty)
        opd2 = man(ox, oy, tx, ty)  # opponent doesn't move during our decision
        adv2 = opd2 - myd2
        # If we can't beat them, still prefer reducing their advantage and moving away from them.
        sep = man(nx, ny, ox, oy)
        score = adv2 * 10 + sep * 0.01 - myd2 * 0.001
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]