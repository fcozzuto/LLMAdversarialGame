def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    best_target = None
    best_key = None
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; otherwise, block nearer-to-them targets.
        adv = opd - myd
        win_flag = 1 if myd <= opd else 0
        key = (win_flag, adv, -myd)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        # No resources visible: drift toward center deterministically.
        best_target = (w // 2, h // 2)

    tx, ty = best_target

    chosen = [0, 0]
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = md(nx, ny, tx, ty)
        opd2 = md(ox, oy, tx, ty)
        # Higher advantage and shorter distance to target.
        key = (-(myd2), (opd2 - myd2), -abs(nx - sx) - abs(ny - sy))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            chosen = [dx, dy]

    if best_move_key is None:
        return [0, 0]
    return chosen