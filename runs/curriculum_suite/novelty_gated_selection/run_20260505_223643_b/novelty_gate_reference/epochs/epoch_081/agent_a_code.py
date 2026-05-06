def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    # Strategy: pick a resource where we can become the "closer arrival" and move to maximize (opp_steps - self_steps),
    # with extra preference for moves that also increase our distance from the opponent (to reduce their contest strength).
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not cell_ok(nx, ny):
            continue
        self_d_op = cheb(nx, ny, ox, oy)
        best_adv = -10**9
        best_r = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Advantage: positive means we are closer (or arrive not later).
            adv = (do - ds)
            # Tie-breakers: prefer targets that are nearer to us and "farther" from opponent after we step.
            adv -= 0.01 * ds
            if adv > best_adv + 1e-12:
                best_adv = adv
                best_r = (rx, ry)
        # If we can't beat them, still pick move that shrinks our arrival time the most and forces opponent away.
        if best_adv < 0:
            # secondary: minimize our distance to the best contested resource
            min_ds = 10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                if ds < min_ds:
                    min_ds = ds
            score = (-min_ds, -self_d_op, -abs((nx - ox)) - abs((ny - oy)))
        else:
            # primary: advantage, then keep some separation from opponent to avoid immediate swaps
            score = (best_adv, -self_d_op, -(abs(best_r[0] - nx) + abs(best_r[1] - ny)) if best_r else 0)
        if best is None or score > best[0]:
            best = (score, dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]