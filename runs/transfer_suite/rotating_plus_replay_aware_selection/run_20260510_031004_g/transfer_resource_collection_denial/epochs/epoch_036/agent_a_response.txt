def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    dirs = [-1, 0, 1]
    moves = []
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best_target = None
    best_primary = None  # higher better
    best_secondary = None  # lower better
    have_adv = False
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        adv = op_d - my_d  # positive means I'm faster/earlier
        if adv > 0:
            have_adv = True
            primary = adv
            secondary = my_d
            if (not have_adv) or (best_primary is None) or primary > best_primary or (primary == best_primary and secondary < best_secondary):
                best_primary, best_secondary = primary, secondary
                best_target = (rx, ry)

    if best_target is None:
        # No resource I reach strictly earlier: pick one with minimal "loss of tempo"
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            my_d = cheb(sx, sy, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            primary = op_d - my_d  # closer to positive is better, but overall favor smallest my_d
            secondary = my_d
            if best_primary is None or primary > best_primary or (primary == best_primary and secondary < best_secondary):
                best_primary, best_secondary = primary, secondary
                best_target = (rx, ry)

    tx, ty = best_target

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        my_d_new = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        # Maximize advantage at next step; tie-break by closer to target, then by dx/dy deterministic order
        val = (op_d - my_d_new, -my_d_new, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]