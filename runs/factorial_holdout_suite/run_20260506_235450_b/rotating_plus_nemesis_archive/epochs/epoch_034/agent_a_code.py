def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Chebyshev distance (diagonal-allowed grid)
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obstacle(x, y):
        # Small penalty for moving adjacent to obstacles
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) in obstacles:
                    return 1
        return 0

    # Pick a target that we can reach earlier than opponent; otherwise best lead attempt
    best = None  # (lead, my_steps, rx, ry)
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        lead = opd - myd  # positive means we can beat opponent
        if best is None or (lead, -myd, -rx, -ry) > (best[0], -best[1], -best[2], -best[3]):
            best = (lead, myd, rx, ry)

    if best is None:
        return [0, 0]
    _, _, tx, ty = best

    # Evaluate one-step moves by improvement in lead to the chosen target, with obstacle proximity penalty
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = dist(nx, ny, tx, ty)
        opd2 = dist(ox, oy, tx, ty)
        lead2 = opd2 - myd2
        val = (lead2, -myd2, -(abs(tx - ox) + abs(ty - oy)), -near_obstacle(nx, ny), -dx, -dy)
        cand.append((val, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True, key=lambda z: z[0])
    return [cand[0][1], cand[0][2]]