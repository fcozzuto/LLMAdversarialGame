def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    best_adv = -10**18
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        adv = opd - myd  # positive if I'm closer
        if adv > best_adv or (adv == best_adv and myd < dist(sx, sy, target[0], target[1]) if target else True):
            best_adv = adv
            target = (rx, ry)

    if target is None:
        target = (w // 2, h // 2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    tx, ty = target

    myd_now = dist(sx, sy, tx, ty)
    opd_now = dist(ox, oy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = dist(nx, ny, tx, ty)
        opd = dist(ox, oy, tx, ty)
        d_op = dist(nx, ny, ox, oy)
        # Prefer reducing my distance to target, while discouraging giving opponent closer access.
        val = (opd - myd) * 10 + (myd_now - myd) * 3 + d_op * 0.2
        # If opponent is already closer to the target, bias toward "stalling" them by increasing distance.
        if opd_now < myd_now:
            val += d_op * 0.8
        # Small tie-break to keep movement deliberate toward target direction.
        val += -(abs((nx - tx)) + abs((ny - ty))) * 0.01
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]