def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def man(ax, ay, bx, by):
        ax = ax - bx
        ay = ay - by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    res = []
    for p in resources:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
            res.append((x, y))
    if not res:
        return [0, 0]

    best = None
    for rx, ry in res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (od - sd, -sd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs_set:
                continue
            d_self = man(nx, ny, tx, ty)
            d_opp = man(ox, oy, tx, ty)
            d_self_now = man(sx, sy, tx, ty)
            step_adv = (d_self_now - d_self)
            score = (step_adv * 10) - (d_self * 2) + (d_opp - d_self) * 0.5
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]
    return best_move