def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        try:
            x, y = int(a[0]), int(a[1])
        except Exception:
            try:
                x, y = int(a.get("x")), int(a.get("y"))
            except Exception:
                continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
        except Exception:
            try:
                x, y = int(r.get("x")), int(r.get("y"))
            except Exception:
                continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    actions = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                actions.append((dx, dy))

    best_action = (0, 0)
    best_val = None
    # Prefer resources we are closer to; also bias toward immediate capture.
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        my_capture = 0
        my_adv = 0
        min_my = 10**9
        best_resource_val = 10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            if myd == 0:
                best_resource_val = -10**9
                break
            opd = cheb(ox, oy, rx, ry)
            # If opponent is much closer, discount that resource.
            val = myd - 0.85 * opd
            if opd <= myd and myd <= 2:
                val += 6  # avoid "contested soon" targets
            if val < best_resource_val:
                best_resource_val = val
                min_my = myd
        my_adv = best_resource_val
        # small penalty for moving away from current best likely area
        for rx, ry in resources:
            if cheb(sx, sy, rx, ry) == min_my:
                my_capture = 1
                break
        # deterministic tie-break: prefer lower min_my, then action order
        val = my_adv + (0 if my_capture else 0.2) + 0.02 * min_my
        if best_val is None or val < best_val:
            best_val = val
            best_action = (dx, dy)

    return [int(best_action[0]), int(best_action[1])]