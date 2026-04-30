def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_dx, best_dy = 0, 0
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # avoid relying on engine rejection

        total = 0.0
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            gap = od - sd  # positive: we are closer than opponent
            # Prioritize swing points: becoming closer than opponent matters more than just being close.
            weight = 1.0 if gap > 0 else 0.55
            total += weight * (gap * 3.0 / (sd + 1))
            # Mild focus to contested resources so we don't drift to irrelevant ones.
            if od < sd:
                total -= (sd - od) * 0.25 / (sd + 1)

        # Deterministic tie-breaker: prefer toward center to avoid being lured into bad diagonals/corners.
        center_bias = - (abs(nx - cx) + abs(ny - cy)) * 0.01
        total += center_bias

        if best_val is None or total > best_val:
            best_val = total
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]