def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # pick target by maximizing current advantage
    best_t = None
    best_adv = None
    best_myd = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        if best_t is None or adv > best_adv or (adv == best_adv and myd < best_myd):
            best_t = (rx, ry)
            best_adv = adv
            best_myd = myd
    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # one-step lookahead: maximize advantage while slightly preferring direct progress to target
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        adv2 = opd2 - myd2
        # if we can grab sooner than opponent in terms of distance, prioritize strongly
        grab_bonus = 0
        if myd2 == 0:
            grab_bonus = 100000
        elif opd2 > myd2:
            grab_bonus = 1000 - myd2
        score = (adv2, -myd2, grab_bonus)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]