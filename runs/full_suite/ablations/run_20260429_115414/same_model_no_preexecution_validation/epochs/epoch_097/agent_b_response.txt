def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    resset = set(resources)
    if (sx, sy) in resset:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy = 0, 0
    best_val = -10**18

    def danger(x, y):
        d = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                if (x + ix, y + iy) in obstacles:
                    d += 1
        return d

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        self_min = 10**9
        opp_min = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            if ds < self_min:
                self_min = ds
            do = cheb(ox, oy, rx, ry)
            if do < opp_min:
                opp_min = do

        # Advantage: become closer to the best available resource compared to opponent
        val = (opp_min - self_min) * 100

        # Extra bias towards capturing sooner
        if self_min == 0:
            val += 10**7
        else:
            val += 20 / (1 + self_min)

        # Obstacle proximity penalty
        val -= danger(nx, ny) * 2

        # Micro-avoid when opponent is also aiming for same nearby resource
        # (push slightly away if opponent is strictly closer to the nearest resource)
        nearest = min(resources, key=lambda r: cheb(nx, ny, r[0], r[1]))
        ds_near = cheb(nx, ny, nearest[0], nearest[1])
        do_near = cheb(ox, oy, nearest[0], nearest[1])
        if do_near < ds_near:
            val -= (ds_near - do_near) * 15

        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]