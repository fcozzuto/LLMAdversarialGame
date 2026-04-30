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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Choose a target deterministically: max (opp_dist - my_dist), then nearest to me
    tx = ty = None
    if resources:
        best_score = -10**18
        best_m = 10**18
        for (x, y) in resources:
            md = man(sx, sy, x, y)
            od = man(ox, oy, x, y)
            score = od - md
            if score > best_score or (score == best_score and md < best_m):
                best_score = score
                best_m = md
                tx, ty = x, y
    else:
        tx, ty = w // 2, h // 2

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18
    tie = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        val = (opd - myd) * 1000 - myd
        if best is None or val > best_val or (val == best_val and (dx, dy) < tie):
            best = [dx, dy]
            best_val = val
            tie = (dx, dy)

    if best is None:
        return [0, 0]
    return best