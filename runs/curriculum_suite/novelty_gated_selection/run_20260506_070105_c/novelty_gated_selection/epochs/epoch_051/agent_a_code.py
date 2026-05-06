def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(o[0]), int(o[1])) for o in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    resources = [r for r in resources if r not in obstacles]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]

    opp_weight = 1.1
    best = None
    for rx, ry in resources:
        my_d = md((sx, sy), (rx, ry))
        op_d = md((ox, oy), (rx, ry))
        # Prefer resources I'm closer to; strongly avoid ones opponent is much closer to.
        # Small tie-break favors being "more aligned" diagonally.
        align = -abs((rx - sx) - (ry - sy))
        score = my_d - opp_weight * op_d + 0.05 * align
        if best is None or score < best[0]:
            best = (score, rx, ry, my_d, op_d)
    _, tx, ty, _, _ = best

    # One-step look: pick move that avoids obstacles and reduces distance to target;
    # also slightly avoids moving toward opponent.
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to = md((nx, ny), (tx, ty))
        d_opp = md((nx, ny), (ox, oy))
        val = d_to - 0.08 * d_opp
        # Deterministic tie-break: prefer smaller |dx| then smaller |dy|, then lexicographic
        tie = (val, abs(dx), abs(dy), dx, dy)
        if best_val is None or tie < best_val:
            best_val = tie
            best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_move