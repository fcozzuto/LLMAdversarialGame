def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    opp_best_to_any = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if opp_best_to_any is None or d < opp_best_to_any:
            opp_best_to_any = d

    best_move = [0, 0]
    best_val = None
    best_tiebreak = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        best_margin = None
        best_my_dist = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - my_d
            if best_margin is None or margin > best_margin or (margin == best_margin and my_d < best_my_dist):
                best_margin = margin
                best_my_dist = my_d

        # Primary: maximize winning margin over opponent for some target.
        # Secondary: reduce my distance to that target.
        # Tertiary: avoid moving away from center-ish (deterministic bias).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = cheb(nx, ny, cx, cy) if isinstance(cx, float) else cheb(nx, ny, int(cx), int(cy))
        my_key = (best_margin, -best_my_dist if best_my_dist is not None else 0, -dist_center)

        if best_val is None or my_key > best_tiebreak:
            best_tiebreak = my_key
            best_move = [dx, dy]
            best_val = best_margin

    return [int(best_move[0]), int(best_move[1])]