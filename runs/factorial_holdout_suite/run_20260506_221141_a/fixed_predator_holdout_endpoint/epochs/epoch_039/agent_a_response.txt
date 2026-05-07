def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_cells = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_cells.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_cells:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    # Pick a target that we can reach sooner than opponent; break ties by being closer.
    best_target = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - myd, -myd, -(rx + ry), -abs(rx - w // 2) - abs(ry - h // 2))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)
    tx, ty = best_target

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_cells:
            cand.append((dx, dy))
    if not cand:
        return [0, 0]

    # Score candidate by improvement on advantage to target and reducing distance to it.
    best_move = cand[0]
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        myd2 = cheb(nx, ny, tx, ty)
        # Approximate opponent distance after our move by current position (deterministic, no prediction).
        opd2 = cheb(ox, oy, tx, ty)
        adv = opd2 - myd2
        # Bonus if we land on any resource.
        res_bonus = 100 if (nx, ny) in resources else 0
        # Small tie-breakers to encourage progress direction to target.
        dir_bonus = -(abs(tx - nx) + abs(ty - ny))
        key = (adv, -myd2, res_bonus, dir_bonus)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]