def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Pick target: prefer resources where we are closer than opponent (positive advantage).
    if resources:
        best_key = None
        best_t = None
        for rx, ry in resources:
            selfd = d2(sx, sy, rx, ry)
            oppd = d2(ox, oy, rx, ry)
            adv = oppd - selfd
            key = (-adv, selfd, rx, ry)  # minimize: negative adv => maximize adv
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
        # Add slight opponent repulsion when the competition is tight.
        comp_tight = d2(sx, sy, ox, oy) <= 10
    else:
        # No visible resources: head toward the nearer side of the board center.
        center_x, center_y = (w - 1) // 2, (h - 1) // 2
        if d2(sx, sy, center_x, center_y) <= d2(ox, oy, center_x, center_y):
            tx, ty = center_x, center_y
        else:
            tx, ty = 0 if sx + ox <= (w - 1) else (w - 1), 0 if sy + oy <= (h - 1) else (h - 1)
        comp_tight = True

    best_move = (0, 0)
    best_val = None
    # Deterministic tie-break order: moves list order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist_to = d2(nx, ny, tx, ty)
        # If tight, gently prefer moving away from opponent.
        dist_from_opp = d2(nx, ny, ox, oy)
        val = dist_to
        if comp_tight:
            val = dist_to - 0.02 * dist_from_opp
        key = (val, abs(dx) + abs(dy), dx, dy)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]