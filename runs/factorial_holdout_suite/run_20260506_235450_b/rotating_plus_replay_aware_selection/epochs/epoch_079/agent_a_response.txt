def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        adv = do - ds  # positive => we are closer
        # If we can't win any race now, contest by minimizing total distance (earlier pickups).
        key = (adv, -(ds + do), -rx, -ry, ds, do)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Prefer moves that increase our advantage and reduce our distance to the target.
    best_move = (0, 0, sx, sy)
    best_eval = None
    for dx, dy, nx, ny in legal:
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        # advantage from current nx,ny vs opponent
        adv2 = do2 - ds2
        # small deterministic tie-breakers to avoid oscillation
        eval_key = (adv2, -ds2, -abs(nx - tx) - abs(ny - ty), dx, dy, nx, ny)
        if best_eval is None or eval_key > best_eval:
            best_eval = eval_key
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]