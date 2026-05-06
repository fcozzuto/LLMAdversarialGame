def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    # Center bias to contest center-rush; deterministic and bounded.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Advantage on resources: prefer decreasing my distance more than opponent's.
        # Also add a small center pressure to avoid drifting.
        adv_best = -10**18
        self_best = 10**18
        opp_best = 10**18
        center_pen = int((abs(nx - cx) + abs(ny - cy)) * 0.25)

        for rx, ry in resources:
            sd = man(nx, ny, sx, sy)  # placeholder for structure; overwrite below
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            if sd < self_best:
                self_best = sd
            if od < opp_best:
                opp_best = od
            adv = od - sd  # higher is better: I get closer than opponent
            if adv > adv_best:
                adv_best = adv

        # Primary: maximize adv_best. Secondary: minimize my distance. Tertiary: center and consistency.
        key = (adv_best, -self_best, -(abs(nx - ox) + abs(ny - oy)), -center_pen, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]