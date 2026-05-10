def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    # Opponent's likely next target (nearest by our metric)
    opp_target = min(resources, key=lambda p: cheb(ox, oy, p[0], p[1]))
    opp_d = cheb(ox, oy, opp_target[0], opp_target[1])
    best_self = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd  # positive => we are closer
        key = (-(margin * 10 + (-sd) * 0.1), sd, -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best_self = (rx, ry)

    # Intercept if opponent is clearly closer to their nearest target
    sd_best_self = cheb(sx, sy, best_self[0], best_self[1])
    sd_opp_target = cheb(sx, sy, opp_target[0], opp_target[1])
    target = best_self
    if sd_opp_target <= opp_d - 1:  # we can start contesting immediately
        target = opp_target
    elif sd_opp_target < sd_best_self:  # fallback: block nearer threat
        target = opp_target

    tx, ty = target
    # Choose among legal neighboring deltas, prefer moves that reduce distance to target and avoid obstacles
    cands = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cands.append((cheb(nx, ny, tx, ty), abs(dx) + abs(dy) * 0.001, -nx, -ny, dx, dy))
    if not cands:
        return [0, 0]
    cands.sort()
    return [int(cands[0][4]), int(cands[0][5])]