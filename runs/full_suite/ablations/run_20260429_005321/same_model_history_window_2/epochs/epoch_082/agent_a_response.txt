def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = None
        best_key = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer we are closer; then deny opponent (larger d_op), then nearer to us
            key = (d_op - d_me, -d_op, -d_me, (rx + ry), -rx)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target()

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None

    # New strategic change: if we can’t secure an advantage, bias toward a "control corridor"
    # by also considering how much the move increases our distance from the opponent.
    target_adv = 0
    if resources:
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_me
            if adv > target_adv:
                target_adv = adv

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_new = cheb(nx, ny, tx, ty)
        d_stay = cheb(sx, sy, tx, ty)
        d_op_after = cheb(ox, oy, tx, ty)
        # Score: improve toward target; also if no advantage, keep distance from opponent
        dist_op_now = cheb(sx, sy, ox, oy)
        dist_op_new = cheb(nx, ny, ox, oy)
        control = (dist_op_new - dist_op_now) if target_adv <= 0 else 0
        score = (-d_new, (d_stay - d_new), -d_op_after, -control, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]