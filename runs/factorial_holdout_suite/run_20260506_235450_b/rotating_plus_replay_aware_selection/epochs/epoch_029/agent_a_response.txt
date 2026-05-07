def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Pick a target that we can reach sooner than the opponent.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # maximize (opponent advantage) then minimize our distance then deterministic tie by coordinate
        key = (od - sd, -sd, -(rx + ry), -rx)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Move greedily to reduce our distance to the chosen target; tie-break by increasing opponent distance.
    best_move = None
    best_key = None
    for dx, dy, nx, ny in legal:
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)  # opponent doesn't change position this turn; use current for consistency
        # Prefer progress (lower nsd). If equal, prefer larger separation (higher nod) and then diagonal/straight bias.
        diag_bonus = 1 if abs(dx) == 1 and abs(dy) == 1 else 0
        # Small additional preference to reduce manhattan to prevent stalling.
        key = (-nsd, nod, diag_bonus, -man(nx, ny, tx, ty), -nx, -ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]