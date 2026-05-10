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

    best = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        score = 0.0
        if (nx, ny) in oppT:
            score += 6.0
        elif (nx, ny) in unclaimed:
            score += 2.0
        elif (nx, ny) in selfT:
            score += 0.5

        dist_op = manh(nx, ny, ox, oy)
        score += -0.06 * dist_op  # prefer moving toward opponent

        dist_center = abs(nx - cx) + abs(ny - cy)
        score += -0.02 * dist_center  # slight center pressure

        # deterministic tie-break
        if score > best_score or (score == best_score and [dx, dy] < best):
            best_score = score
            best = [dx, dy]

    return best