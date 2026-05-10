def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_cell = (sx, sy)
    best_cell_score = None

    if not resources:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # For this next cell, pick the resource that maximizes "I arrive first" pressure.
        # Higher score is better: larger distance advantage + closeness + slight preference for central resources.
        local_best = None
        for rx, ry in res:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            advantage = opd - myd  # positive if I am closer
            # Obstacle proximity penalty (cheap deterrent): steer away from stepping adjacent to obstacles
            prox = 0
            for ax, ay in obstacles_list:
                if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                    prox += 1
            central = - (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)) * 0.01
            # Encourage immediate collection: if in same cell, very high score.
            collect_bonus = 1000 if (nx == rx and ny == ry) else 0
            key_score = (advantage * 10.0) + (-myd * 1.0) + central + collect_bonus + (-prox * 0.5)
            if local_best is None or key_score > local_best:
                local_best = key_score

        if best_cell_score is None or local_best > best_cell_score:
            best_cell_score = local_best
            best_cell = (nx, ny)

    return [best_cell[0] - sx, best_cell[1] - sy]