def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        contest = opd - myd  # bigger => we are closer
        # Prefer higher contest, then smaller myd, then farther from opponent, then deterministic coord
        key = (-contest, myd, -opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(0, 0)]
    sdx = 0 if tx == sx else (1 if tx > sx else -1)
    sdy = 0 if ty == sy else (1 if ty > sy else -1)
    cand += [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Put the most direct direction earlier for determinism/strength
    direct = (sdx, sdy)
    cand2 = [direct, (sdx, 0), (0, sdy), (sdx, -sdy), (-sdx, sdy), (-sdx, 0), (0, -sdy), (0, 0)]
    seen = set()
    order = []
    for d in cand2 + cand:
        if d not in seen:
            seen.add(d)
            order.append(d)

    best_move = (0, 0)
    best_val = None
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        new_myd = cheb(nx, ny, tx, ty)
        new_opd = cheb(ox, oy, tx, ty)
        new_contest = new_opd - new_myd
        # Maximize contest, then minimize distance; deterministic integer scoring
        val = new_contest * 10000 - new_myd * 10 - cheb(nx, ny, ox, oy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]