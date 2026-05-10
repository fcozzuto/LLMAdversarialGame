def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    turns_remaining = int(observation.get("turns_remaining", 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort(key=lambda d: (d[0] == 0 and d[1] == 0, abs(d[0]) + abs(d[1])))

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        best = (-10**9, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            sc = -cheb(nx, ny, tx, ty) + 0.03 * cheb(nx, ny, ox, oy)
            if sc > best[0]:
                best = (sc, (dx, dy))
        return [best[1][0], best[1][1]]

    best_sc, best_move = -10**18, (0, 0)
    base_moves = deltas

    for dx, dy in base_moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Find best contested/available resource after this move.
        best_here = -10**18
        for rx, ry in resources:
            sd0 = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            sd1 = cheb(nx, ny, rx, ry)

            # Primary: increase opponent-self distance gap (prefer states where we are closer).
            gap = od - sd1

            # Secondary: prefer immediate progress to reduce our distance.
            prog = sd0 - sd1

            # Tertiary: slight preference for closer completion when turns run out.
            urgency = 0.02 * (turns_remaining <= 6) * (-sd1)

            # Penalize moves that would keep us from ever improving (small deterministic nudge).
            stay_pen = 0.0
            if dx == 0 and dy == 0 and sd1 >= sd0:
                stay_pen = -0.5

            sc = 1.2 * gap + 0.35 * prog + urgency + stay_pen
            if sc > best_here:
                best_here = sc

        if best_here > best_sc:
            best_sc, best_move = best_here, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]