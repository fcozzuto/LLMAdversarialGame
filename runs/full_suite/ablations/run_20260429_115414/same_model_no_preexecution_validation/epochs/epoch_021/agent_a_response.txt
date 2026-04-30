def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs_set

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        if not obs_set:
            return 0.0
        m = 99
        for px, py in obs_set:
            d = cheb(x, y, px, py)
            if d < m:
                m = d
                if m <= 1:
                    break
        if m <= 1:
            return 2.8
        if m == 2:
            return 1.1
        return 0.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best, bestv = (0, 0), -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Drift to center while keeping distance to opponent.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            v = -cheb(nx, ny, int(cx), int(cy)) + 0.25 * cheb(nx, ny, ox, oy) - obs_pen(nx, ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [int(best[0]), int(best[1])]

    # Target selection: go for resource where we can gain the most race advantage.
    target = resources[0]
    best_adv = -10**18
    any_pos = False
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # positive means I'm closer
        if adv > 0:
            any_pos = True
        if adv > best_adv:
            best_adv = adv
            target = (rx, ry)

    # Move selection: minimize (next_my_dist - opp_dist_to_target) while also avoiding obstacles.
    tx, ty = target
    best, bestv = (0, 0), 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_next = cheb(nx, ny, tx, ty)
        opp_now = cheb(ox, oy, tx, ty)
        # Also slightly prefer moves that increase separation from opponent to avoid being out-positioned.
        v = (my_next - opp_now) + 0.08 * (-cheb(nx, ny, ox, oy)) + 0.9 * obs_pen(nx, ny)
        if v < bestv:
            bestv, best = v, (dx, dy)

    return [int(best[0]), int(best[1])]