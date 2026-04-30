def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    # Choose a target resource where we are most ahead (largest distance advantage).
    best_t = None
    best_adv = None
    best_myd = None
    for tx, ty in resources:
        myd = dist(sx, sy, tx, ty)
        opd = dist(ox, oy, tx, ty)
        adv = opd - myd
        key = (adv, -myd, tx, ty)
        if best_t is None or key > (best_adv, best_myd, best_t[0], best_t[1]):
            best_t = (tx, ty)
            best_adv = adv
            best_myd = myd

    tx, ty = best_t

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = dist(nx, ny, tx, ty)
        opd = dist(nx, ny, ox, oy)
        # Primary: minimize distance to target; Secondary: push away from opponent; Tertiary: progress advantage.
        score = (-myd, opd, (dist(ox, oy, tx, ty) - myd), -abs(nx - tx) - abs(ny - ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]