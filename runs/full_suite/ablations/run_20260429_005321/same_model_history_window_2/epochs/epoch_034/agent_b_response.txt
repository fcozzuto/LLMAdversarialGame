def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_t = None
        best_key = None
        for tx, ty in resources:
            ds = man(sx, sy, tx, ty)
            do = man(ox, oy, tx, ty)
            adv = do - ds  # positive => we are closer
            key = (-adv, ds, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        # No visible resources: head toward opponent-facing center to contest space
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = man(nx, ny, tx, ty)
        do_next = man(nx, ny, ox, oy)
        # Prefer approaching target; penalize moving into opponent-favored proximity
        opp_current = man(sx, sy, ox, oy)
        val = (ds_next, -do_next, abs(do_next - opp_current), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if not isinstance(dx, int) or not isinstance(dy, int):
        return [0, 0]
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]