def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    # Target from each candidate: resource that we can reach fastest; prefer moves where we are not behind opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        self_best_d = 10**9
        opp_at_self_best = 10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = man(nx, ny, rx, ry)
            if sd < self_best_d:
                self_best_d = sd
                opp_at_self_best = man(ox, oy, rx, ry)
        # If self is closer than opponent, good. If behind, bad. Also lightly prefer progress.
        lead = opp_at_self_best - self_best_d  # higher is better
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        # Primary: maximize lead, Secondary: minimize self_best_d, Tertiary: avoid staying.
        key = (-lead, self_best_d, stay_pen, abs(dx) + abs(dy))
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]