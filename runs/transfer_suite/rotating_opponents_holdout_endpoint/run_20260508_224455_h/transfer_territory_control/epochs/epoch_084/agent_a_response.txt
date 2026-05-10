def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    def to_set(lst):
        s = set()
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obst = to_set(observation.get("obstacles"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    cx, cy = w // 2, h // 2

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Prefer solid expansion/coverage; opportunistically flip only if it also moves toward the center.
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        score = 0.0
        if (nx, ny) in oppT:
            # Flip is valuable, but only take it when it helps control the middle and doesn't suicide into opponent.
            score += 3.5
            score += 0.20 * (manh(nx, ny, cx, cy) * -1)
            score += 0.10 * (manh(nx, ny, ox, oy) * -1)
        elif (nx, ny) in unclaimed:
            score += 1.4
            score += 0.12 * (manh(nx, ny, cx, cy) * -1)
            score += 0.03 * (manh(nx, ny, ox, oy) * 1)
        elif (nx, ny) in selfT:
            score += 0.25
            score += 0.06 * (manh(nx, ny, cx, cy) * -1)
            score += 0.04 * (manh(nx, ny, ox, oy) * 1)
        else:
            # Neutral/unknown cell
            score += 0.15
            score += 0.08 * (manh(nx, ny, cx, cy) * -1)

        # Mild anti-contact: don't step into squares that are adjacent to many opponent-territory cells.
        adj_opp = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if inside(tx, ty) and (tx, ty) in oppT:
                adj_opp += 1
        score -= 0.10 * adj_opp

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move