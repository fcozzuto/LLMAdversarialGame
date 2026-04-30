def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                resources.append((rx, ry))

    if not resources:
        bestd = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, (w - 1) / 2, (h - 1) / 2)
            if v > bestv or (v == bestv and (dx, dy) < bestd):
                bestv, bestd = v, (dx, dy)
        return [bestd[0], bestd[1]]

    best_next = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Primary goal: reduce distance to resources.
        min_d = 10**9
        tie_best = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < min_d or (d == min_d and (rx, ry) < tie_best):
                min_d = d
                tie_best = (rx, ry)
        rx, ry = tie_best

        # Secondary: bias toward resources we can reach no later than opponent.
        du = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        reach_bonus = 4 if du <= do else -2

        # Tertiary: steer to resources that are "less contested" overall.
        contest = 0
        for ax, ay in resources:
            if (ax, ay) == (rx, ry):
                continue
            contest += 1 if cheb(ox, oy, ax, ay) <= cheb(nx, ny, ax, ay) else 0

        # Mild obstacle-near penalty by counting blocked neighbors.
        adj_blocked = 0
        for mx, my in dirs:
            px, py = nx + mx, ny + my
            if not (0 <= px < w and 0 <= py < h) or (px, py) in blocked:
                adj_blocked += 1

        val = (-min_d * 2.0) + reach_bonus - contest * 0.4 - adj_blocked * 0.05
        if val > best_val or (val == best_val and (dx, dy) < best_next):
            best_val = val
            best_next = (dx, dy)

    return [int(best_next[0]), int(best_next[1])]