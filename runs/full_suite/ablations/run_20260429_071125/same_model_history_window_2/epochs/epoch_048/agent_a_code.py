def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    vx, vy = ox - sx, oy - sy
    if vx == 0 and vy == 0:
        vx, vy = 1, 1
    steps = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_t = None
    best_k = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # positive => we are closer
        # deterministic sweep bias toward opponent corner (helps change policy vs pure advantage)
        ax = rx - sx
        ay = ry - sy
        proj = ax * vx + ay * vy
        # prefer strong advantage; if tied, prefer closer and more aligned
        k = (-(adv), myd, -proj, rx, ry)
        if best_k is None or k < best_k:
            best_k, best_t = k, (rx, ry)
    tx, ty = best_t

    best_m = None
    best_mv = None
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # minimize our distance; lightly penalize if opponent would be even more favored
        mv = (myd2, opd2 - myd2, abs(dx) + abs(dy), dx, dy)
        if best_mv is None or mv < best_mv:
            best_mv, best_m = mv, [dx, dy]
    return best_m if best_m is not None else [0, 0]