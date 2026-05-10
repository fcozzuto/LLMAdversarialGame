def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
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

    best = None
    best_key = None
    for rx, ry in resources:
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        adv = opp_d - self_d
        key = (adv, -self_d, min(self_d, opp_d), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    pref = (sign(tx - sx), sign(ty - sy))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                moves.append((dx, dy))

    def dist_to_target(dx, dy):
        return cheb(sx + dx, sy + dy, tx, ty)

    # Try preferred direction first; otherwise pick best deterministic among legal moves
    candidates = []
    for dx, dy in moves:
        d = dist_to_target(dx, dy)
        closer_bonus = 1 if d < cheb(sx, sy, tx, ty) else 0
        key = (d, -closer_bonus, dx, dy)
        candidates.append((key, [dx, dy]))
    candidates.sort(key=lambda x: x[0])
    # Ensure we don't get stuck if preferred move is legal
    if pref in [tuple(m[1]) for m in candidates]:
        return [pref[0], pref[1]]
    return candidates[0][1]