def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best_mv = (0, 0)
        best_val = -10**18
        alpha = 0.9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            my_dist = 10**9
            for rx, ry in resources:
                d_self = man(nx, ny, rx, ry)
                d_opp = man(ox, oy, rx, ry)
                # Smaller is better; reward being closer than opponent.
                score = d_self - alpha * d_opp
                if score < my_dist:
                    my_dist = score
            # Prefer immediate resource pickup when standing on it.
            on_res = 1 if (nx, ny) in obstacles else 0
            val = -my_dist + (1 if any((nx == rx and ny == ry) for rx, ry in resources) else 0) - on_res * 10
            if val > best_val:
                best_val = val
                best_mv = (dx, dy)
        return [int(best_mv[0]), int(best_mv[1])]

    # No visible resources: reposition to maximize distance from opponent while staying centered.
    cx, cy = w // 2, h // 2
    best_mv = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)
        d_center = man(nx, ny, cx, cy)
        val = d_opp * 2 - d_center
        if val > best_val:
            best_val = val
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]