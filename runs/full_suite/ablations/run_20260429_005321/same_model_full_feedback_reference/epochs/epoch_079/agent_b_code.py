def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Choose a target resource that we can reach earlier than opponent, else fallback to nearest.
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        myd = dist2(sx, sy, rx, ry)
        opd = dist2(ox, oy, rx, ry)
        # Prefer resources where we're closer; slightly prefer far from opponent to avoid contest.
        score = (opd - myd) * 10 - myd + (myd < opd) * 500
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = (1, 1) if best_t is None else best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_mscore = -10**18

    # Deterministically evaluate immediate move quality with contest + obstacle safety.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = dist2(nx, ny, tx, ty)
        opd = dist2(nx, ny, ox, oy)
        # Encourage approach to target; discourage getting too close to opponent.
        contest = dist2(ox, oy, tx, ty) - myd
        mscore = -myd + contest * 8 + opd * 0.6
        # If resources exist, also slightly prefer not moving away when on same diagonal/line.
        if resources:
            sx2 = 1 if tx > nx else (-1 if tx < nx else 0)
            sy2 = 1 if ty > ny else (-1 if ty < ny else 0)
            align = (dx == sx2) + (dy == sy2)
            mscore += align * 6
        if mscore > best_mscore:
            best_mscore = mscore
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]