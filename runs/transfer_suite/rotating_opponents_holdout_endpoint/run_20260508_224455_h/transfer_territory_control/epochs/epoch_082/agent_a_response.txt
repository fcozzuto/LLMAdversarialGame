def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    def make_set(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obst = make_set(observation.get("obstacles"))
    selfT = make_set(observation.get("self_territory"))
    oppT = make_set(observation.get("opponent_territory"))
    unclaimed = make_set(observation.get("unclaimed_cells"))

    cx, cy = w // 2, h // 2
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x, y, a, b):
        dx = x - a
        if dx < 0:
            dx = -dx
        dy = y - b
        if dy < 0:
            dy = -dy
        return dx + dy

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        score = 0
        # Territory control priority
        if (nx, ny) in selfT:
            score += 6
        if (nx, ny) in oppT:
            score += 55  # likely capture on entry
        if (nx, ny) in unclaimed:
            score += 75  # claim potential

        # Move toward center, but avoid walking into opponent if it doesn't improve capture
        dc = manh(nx, ny, cx, cy)
        do = manh(nx, ny, ox, oy)
        score += (80 - dc) * 2
        score += do * 1  # bias away from being too close unless capturing

        # If we have no territory elsewhere, favor direct approach
        if not selfT:
            score += (80 - manh(nx, ny, cx, cy)) * 3

        # Small tie-break: deterministic preference order already fixed by list, but add numeric
        score += (-dx * 0.01 - dy * 0.001)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move