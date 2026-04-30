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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a target resource that we can contest (prefer where opponent is relatively far).
    best_t = resources[0]
    best_contest = -10**9
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        contest = (opd - myd)  # higher => we are closer / opponent farther
        if contest > best_contest:
            best_contest = contest
            best_t = (rx, ry)

    tx, ty = best_t
    best_move = (0, 0)
    best_val = -10**18

    res_set = set(resources)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        myd_now = cheb(sx, sy, tx, ty)

        # Aim to reduce distance to target, while increasing separation from opponent on contest.
        val = (opd - myd) - 0.25 * myd

        # If we step onto any resource, prioritize strongly.
        if (nx, ny) in res_set:
            val += 20

        # If we are moving away from target, penalize.
        if myd > myd_now:
            val -= 2

        # Mild center bias for tie-breaking (deterministic).
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        val -= 0.001 * dist_center

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]