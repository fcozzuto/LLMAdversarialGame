def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def obs_pen(x, y):
        # small deterministic penalty for moving close to obstacles
        pen = 0
        for ax, ay in obstacles:
            dx = ax - x
            dy = ay - y
            if dx * dx + dy * dy <= 4:
                pen += 1
        return pen

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    best = (10**18, None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # core: race resources, try to arrive earlier than opponent
        if resources:
            best_r = None
            best_r_score = 10**18
            for rx, ry in resources:
                d_our = dist2(nx, ny, rx, ry)
                d_opp = dist2(ox, oy, rx, ry)
                # prefer immediate pickup, then winning the race
                pickup_bonus = -10**6 if d_our == 0 else 0
                score = (d_our - d_opp) + pickup_bonus + 0.05 * d_our
                if score < best_r_score:
                    best_r_score = score
                    best_r = (rx, ry)
            # tie-break toward progressing diagonally away from start-opponent distance
            prog = dist2(nx, ny, ox, oy)
            score_total = best_r_score + 0.1 * prog + 0.8 * obs_pen(nx, ny)
        else:
            # fallback: head toward center-ish while avoiding obstacles
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score_total = dist2(nx, ny, cx, cy) + 0.8 * obs_pen(nx, ny)

        if score_total < best[0] or (score_total == best[0] and (dx, dy) < best[1]):
            best = (score_total, (dx, dy))

    if best[1] is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]