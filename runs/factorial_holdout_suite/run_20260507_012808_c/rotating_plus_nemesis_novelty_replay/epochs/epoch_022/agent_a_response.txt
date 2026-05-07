def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer moves that win tempo on contested resources, while avoiding stepping into immediate danger.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    my = (sx, sy)
    opp = (ox, oy)

    # Preselect a small deterministic subset to keep computation light.
    resources_sorted = sorted(resources, key=lambda p: dist(my, p))
    candidates = resources_sorted[:min(6, len(resources_sorted))]

    # Simple obstacle proximity penalty (encourages safer routes without full search).
    def obstacle_penalty(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    pen += 2
        return pen

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        cur = (nx, ny)

        score = 0.0
        # Tempo advantage: how much sooner we can reach a resource than opponent.
        for r in candidates:
            t_me = dist(cur, r)
            t_op = dist(opp, r)
            if t_me == 0 and t_op > 0:
                score += 50.0
            adv = t_op - t_me
            if adv > 0:
                score += adv / (1 + t_me)

        # Discourage moving toward opponent if it doesn't improve tempo (tends to cause harmless cycles).
        d0 = dist(my, opp)
        d1 = dist(cur, opp)
        if d1 > d0:
            score += 0.15 * (d1 - d0)
        else:
            score -= 0.05 * (d0 - d1)

        score -= 0.15 * obstacle_penalty(nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]