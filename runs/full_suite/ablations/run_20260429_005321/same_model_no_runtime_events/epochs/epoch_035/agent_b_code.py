def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        best_key = None
        for (rx, ry) in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where we are closer; tie-break by being overall nearer.
            key = (-(1 if ds < do else 0), ds - do, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = man(nx, ny, tx, ty)
        # If resources exist, improve over opponent on contested targets.
        contest_bonus = 0
        if resources:
            # Use a small deterministic look at the best contested resource from the next state.
            local_best = None
            local_key = None
            for (rx, ry) in resources:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                key = (-(1 if ds < do else 0), ds - do, ds, rx, ry)
                if local_key is None or key < local_key:
                    local_key = key
                    local_best = (rx, ry)
            rx, ry = local_best
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            contest_bonus = 2 if ds < do else 0
        # Score: primary minimize distance to target; slight preference to reducing opponent relative distance.
        rel = 0
        if resources:
            rel = man(ox, oy, tx, ty) - man(nx, ny, tx, ty)
        val = (ds_next, -contest_bonus, -rel, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]