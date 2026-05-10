def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    dirs_sorted = sorted(dirs, key=lambda d: (d[0], d[1]))

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in dirs_sorted:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            d = dist8(nx, ny, cx, cy)
            key = (d, nx, ny)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    res = [tuple(p) for p in resources]
    best = None
    for dx, dy in dirs_sorted:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Greedy-advantage: prefer resources where we are closer than opponent after this move.
        # Score candidate: lower is better.
        # If we can reach a resource with clear advantage, it dominates; otherwise, we minimize our distance
        # while also keeping opponent distances relatively large.
        total = 0
        reachable_bonus = 0
        for rx, ry in res:
            ds = dist8(nx, ny, rx, ry)
            do = dist8(ox, oy, rx, ry)
            adv = ds - do  # negative means we are closer
            if ds == 0:
                return [dx, dy]
            # Strongly prioritize negative adv; discourage positive adv.
            w_adv = 20 if adv <= 0 else 40
            # Encourage getting closer, but only matter when not already blocked by disadvantage.
            total += w_adv * (ds + max(0, adv))
            if adv <= 0:
                reachable_bonus += max(0, 8 - ds)

        # tie-break deterministically with coordinates
        key = (-(reachable_bonus), total, dist8(nx, ny, w - 1, h - 1), nx, ny, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]]