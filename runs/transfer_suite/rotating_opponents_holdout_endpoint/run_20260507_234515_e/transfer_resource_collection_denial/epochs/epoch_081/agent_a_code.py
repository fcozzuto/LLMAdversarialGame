def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev: diagonal movement allowed

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    # Evaluate by Chebyshev advantage; if we can't secure it, choose move that reduces opponent advantage.
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        local_best = -10**18
        for rx, ry in resources:
            self_d = cd(nx, ny, rx, ry)
            opp_d = cd(ox, oy, rx, ry)

            # Obstacle pressure: encourage routes away from closest obstacle (local deterrent).
            # (Deterministic and cheap; not a full pathfinder.)
            min_ob_d = 10**9
            for ax, ay in obstacles:
                dd = cd(nx, ny, ax, ay)
                if dd < min_ob_d:
                    min_ob_d = dd
            obstacle_pen = 0 if min_ob_d >= 2 else (2 - min_ob_d) * 0.25

            advantage = (opp_d - self_d)
            # Prefer resources we can reach strictly sooner; otherwise deny/contend.
            reach_bonus = 2.0 if self_d < opp_d else (0.0 if self_d == opp_d else -0.5)
            score = advantage * 1.6 + reach_bonus - obstacle_pen

            # Slight tie-break toward closer own distance (faster pickup).
            score -= self_d * 0.05
            if score > local_best:
                local_best = score

        if local_best > best_score:
            best_score = local_best
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]