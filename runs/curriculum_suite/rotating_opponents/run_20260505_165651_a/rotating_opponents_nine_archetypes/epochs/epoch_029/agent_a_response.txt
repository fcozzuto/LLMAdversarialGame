def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def opp_best_after1_to(rx, ry):
        best = 10**9
        for ddx, ddy in moves:
            nx, ny = ox + ddx, oy + ddy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = king_dist(nx, ny, rx, ry)
            if d < best:
                best = d
        return best if best < 10**9 else king_dist(ox, oy, rx, ry)

    def obstacle_pressure(x, y):
        p = 0
        for ddx, ddy in moves:
            nx, ny = x + ddx, y + ddy
            if (nx, ny) in obstacles:
                p += 1
        return p

    if not resources:
        return [0, 0]

    best_s = -10**18
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_step_best = -10**18
        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            oppd1 = opp_best_after1_to(rx, ry)
            adv = oppd1 - myd  # positive: we are closer even after opponent's next step
            s = 12 * adv - myd
            if myd == 0:
                s += 1000
            my_step_best = s if s > my_step_best else my_step_best

        s_total = my_step_best - 2.0 * obstacle_pressure(nx, ny)
        key = (s_total, -king_dist(nx, ny, ox, oy), -dx, -dy)
        if key > (best_s, -10**9, -best[0], -best[1]):
            best_s = s_total
            best = (dx, dy)

    return [int(best[0]), int(best[1])]