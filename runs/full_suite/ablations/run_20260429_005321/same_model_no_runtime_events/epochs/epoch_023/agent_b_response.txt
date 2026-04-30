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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # Disruption: move to reduce distance to opponent-middle line
        tx = (ox + (w - 1 - ox)) // 2
        ty = (oy + (h - 1 - oy)) // 2
        tx = (tx + w // 2) // 2
        ty = (ty + h // 2) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - (0.2 * (dx != 0 or dy != 0))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Choose move via 1-step evaluation towards a resource where opponent is not strictly ahead.
    # Aim: maximize (op_dist - my_dist) to win races; if losing, try to reduce opponent's lead.
    best_move = [0, 0]
    best_val = -10**18
    res_list = resources

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        my_best = -10**18
        for (rx, ry) in res_list:
            od = cheb(ox, oy, rx, ry)
            md = cheb(nx, ny, rx, ry)
            # Primary: win race (bigger lead for us). Secondary: avoid very far targets.
            lead = od - md
            # Tiebreak: slightly prefer closer md when lead ties; also prefer targets closer to center.
            center = cheb(nx, ny, w // 2, h // 2)
            v = lead * 1000 - md * 2 - center * 0.1
            if v > my_best:
                my_best = v

        # Small penalty for staying still so we keep changing policy effectually when behind.
        v_total = my_best - (0.15 if dx == 0 and dy == 0 else 0.0)
        # Deterministic tie-break: prefer earlier dirs order already, so only '>'.
        if v_total > best_val:
            best_val = v_total
            best_move = [dx, dy]

    return best_move