def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_evader = not any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y, tx, ty):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx >= dy else dy

    # Candidate corner targets for evader (farthest from opponent)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    corners.sort(key=lambda c: (-cheb(c[0], c[1], ox, oy), c[0], c[1]))

    # If any corner is blocked, it naturally won't be targeted; we just use distance.
    best_move = (0, 0, -10**9 if i_am_evader else 10**9)
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    # Deterministic move evaluation
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue

            if i_am_evader:
                # Prefer moves that (1) maximize separation from opponent, (2) head toward best corner target.
                sep = cheb(nx, ny, ox, oy)
                tx, ty = corners[0]
                toward = -cheb(nx, ny, tx, ty)  # higher is better (less distance)
                score = sep * 10 + toward
                if score > best_move[2]:
                    best_move = (dx, dy, score)
            else:
                # Pursuer: minimize separation from opponent, lightly bias toward center to avoid corner traps.
                sep = cheb(nx, ny, ox, oy)
                center_bias = -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)
                score = sep * 10 + (-center_bias)  # lower is better
                if score < best_move[2]:
                    best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]