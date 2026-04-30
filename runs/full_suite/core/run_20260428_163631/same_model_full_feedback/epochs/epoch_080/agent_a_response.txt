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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if resources:
        best_t = None
        best_v = None
        # Target resource that maximizes (opponent advantage over me) we can flip,
        # also prefer being close to it.
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If opponent is much closer, avoid unless we are also relatively close.
            v = (od - myd) * 10 - myd
            # Small bias to avoid always chasing same side: prefer towards center slightly.
            v += -0.1 * cheb(rx, ry, cx, cy)
            if best_v is None or v > best_v or (v == best_v and (rx, ry) < best_t):
                best_v = v
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = cx, cy

    # Evaluate next step: maximize reduction in distance to chosen target while
    # also trying to increase opponent distance to that same target.
    best_m = (0, 0)
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd0 = cheb(sx, sy, tx, ty)
        myd1 = cheb(nx, ny, tx, ty)
        od0 = cheb(ox, oy, tx, ty)
        od1 = cheb(ox, oy, tx, ty)  # opponent doesn't move this step in evaluation
        # Primary: get closer to target
        s = (myd0 - myd1) * 100
        # Secondary: if tie, prefer moves that make opponent less likely to get the target next
        # by improving my relative advantage to that target.
        s += (od0 - myd1) * 3
        # Tertiary: avoid getting too far from center to keep mobility
        s += -0.01 * cheb(nx, ny, cx, cy)
        if best_s is None or s > best_s or (s == best_s and (dx, dy) < best_m):
            best_s = s
            best_m = (dx, dy)

    # If all moves blocked (unlikely), stay put.
    return [int(best_m[0]), int(best_m[1])]