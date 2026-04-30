def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def greedy_step(px, py, tx, ty):
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if blocked(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return best[0], best[1]

    if not resources:
        cx = (gw - 1) // 2
        cy = (gh - 1) // 2
        # If we are far from center, head to center; otherwise head to opponent.
        if cheb(sx, sy, cx, cy) > cheb(sx, sy, ox, oy):
            tx, ty = cx, cy
        else:
            tx, ty = ox, oy
        dx0, dy0 = greedy_step(sx, sy, tx, ty)
        return [int(dx0), int(dy0)]

    best_move = (0, 0)
    best_val = -10**18

    # Deterministic tie-break uses (dx,dy) ordering via lexicographic comparison.
    for dx0, dy0 in moves:
        nsx, nsy = sx + dx0, sy + dy0
        if blocked(nsx, nsy):
            continue

        cur_best = -10**18
        for rx, ry in resources:
            odx, ody = greedy_step(ox, oy, rx, ry)
            nox, noy = ox + odx, oy + ody
            self_d = cheb(nsx, nsy, rx, ry)
            opp_d = cheb(nox, noy, rx, ry)
            # Positive means we get closer than opponent to the same resource.
            adv = (opp_d - self_d)
            # Small preference for reducing absolute self distance and favoring center slightly.
            center_x = (gw - 1) // 2
            center_y = (gh - 1) // 2
            adv += 0.05 * (cheb(ox, oy, center_x, center_y) - cheb(nsx, nsy, center_x, center_y))
            adv -= 0.01 * self_d
            if adv > cur_best:
                cur_best = adv

        if cur_best > best_val or (cur_best == best_val and (dx0, dy0) < best_move):
            best_val = cur_best
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best