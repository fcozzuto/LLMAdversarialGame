def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        best_score = -10**18
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            rel = opd - myd  # positive means we are closer than opponent
            # Prefer nearer when relative ties; include slight distance from opponent overall
            score = rel * 100 - myd - 0.1 * cheb(ox, oy, rx, ry)
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources: head toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_tuple = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        if (nx, ny) == (tx, ty):
            myd2 -= 1  # strong preference to step onto target
        # Tie-break: reduce opponent access to same target, and stay away from obstacles implicitly via free()
        oppd2 = cheb(ox, oy, tx, ty)
        # Prefer moves that increase our lead (or reduce opponent advantage)
        lead = oppd2 - myd2
        t = (myd2, -lead, cheb(nx, ny, ox, oy), dx, dy)
        if best_tuple is None or t < best_tuple:
            best_tuple = t
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]