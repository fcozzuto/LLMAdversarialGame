def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = [tuple(p) for p in observation.get("resources", [])]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def safe(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = -10**30
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not safe(nx, ny):
            continue

        if resources:
            my_best = -10**30
            for rx, ry in resources:
                myd = cheb((nx, ny), (rx, ry))
                opd = cheb((ox, oy), (rx, ry))
                adv = (opd - myd)
                # prefer winning the resource (adv large), then closer overall
                val = adv * 100 - myd * 3
                # small tie-break: prefer resources more central to both
                center = cheb((rx, ry), (cx, cy))
                val -= center * 0.2
                if val > my_best:
                    my_best = val
            # encourage moving toward a good direction; tiny preference toward center if tie
            myd_center = cheb((nx, ny), (cx, cy))
            val2 = my_best - myd_center * 0.01
        else:
            # no resources: reduce distance to opponent to potentially deny
            val2 = -cheb((nx, ny), (ox, oy)) - cheb((nx, ny), (cx, cy)) * 0.05

        if val2 > best:
            best = val2
            best_move = [dx, dy]

    return best_move