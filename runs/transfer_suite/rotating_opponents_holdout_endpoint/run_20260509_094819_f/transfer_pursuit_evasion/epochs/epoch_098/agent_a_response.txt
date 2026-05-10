def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    evader = ("evader" in sr) or ("escape" in sr) or ("runner" in sr) or ("evasion" in sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if evader:
        target_corner = min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
    else:
        target_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))

    def obstacle_penalty(nx, ny):
        pen = 0
        if blocked:
            for (bx, by) in blocked:
                d = cheb(nx, ny, bx, by)
                if d == 0:
                    return 10**6
                if d == 1:
                    pen += 3
                elif d == 2:
                    pen += 1
        return pen

    best = None
    best_score = None
    sign = 1 if evader else -1  # maximize distance when evader, minimize when pursuer

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, target_corner[0], target_corner[1])
        pen = obstacle_penalty(nx, ny)

        # Wall-run-ish bias: prefer continuing toward the chosen corner and away from blocked tiles.
        # Tie-break deterministically with (dx,dy).
        score = sign * d_opp - 0.05 * d_corner - pen * 0.01
        if best_score is None or (score > best_score if evader else score < best_score):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best