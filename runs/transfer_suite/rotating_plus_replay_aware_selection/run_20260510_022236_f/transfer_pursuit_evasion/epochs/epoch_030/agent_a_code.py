def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) and ("purs" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def openness(x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    # Obstacle-aware target: farthest/nearest corner from opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        target = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        target = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    # Also bias along a corridor away/toward the target without doing full search.
    tx, ty = target

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = dist2(nx, ny, tx, ty)
        opn = openness(nx, ny)

        # Small deterministic obstacle proximity penalty (discourages hugging walls).
        wall_pen = 0
        for obx, oby in obs:
            dd = abs(nx - obx) + abs(ny - oby)
            if dd == 0:
                wall_pen += 100000
            elif dd == 1:
                wall_pen += 3
            elif dd == 2:
                wall_pen += 1

        # If roles align as evader: maximize distance to pursuer and move toward far-corner.
        # If pursuer: minimize distance to evader and move toward evader's side.
        if is_evader:
            val = (d_opp * 10) + (d_tgt * -0.25) + (opn * 2) - wall_pen
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < tuple(best_move))
        else:
            val = (d_opp * -10) + (d_tgt * -0.05) + (opn * 2) - wall_pen
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < tuple(best_move))

        if better:
            best_val = val
            best_move = [dx, dy]

    return best_move