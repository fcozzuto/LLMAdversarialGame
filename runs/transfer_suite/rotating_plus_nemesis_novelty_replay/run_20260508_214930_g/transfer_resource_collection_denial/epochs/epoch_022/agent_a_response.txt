def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2
    best = None
    tx = ty = None

    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        win = oppd - myd
        center = cheb(rx, ry, cx, cy)
        key = (win, -myd, -center, -(rx * h + ry))
        if best is None or key > best:
            best = key
            tx, ty = rx, ry

    if tx is None:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_myd = cheb(sx, sy, tx, ty)
    cur_oppd = cheb(ox, oy, tx, ty)

    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        myd = cheb(nx, ny, tx, ty)
        adv_new = cur_oppd - myd
        step_bonus = 1 if myd < cur_myd else 0
        move_center = cheb(nx, ny, cx, cy)
        score = (adv_new, step_bonus, -move_center, -cheb(nx, ny, tx, ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [nx - sx, ny - sy]

    return best_move