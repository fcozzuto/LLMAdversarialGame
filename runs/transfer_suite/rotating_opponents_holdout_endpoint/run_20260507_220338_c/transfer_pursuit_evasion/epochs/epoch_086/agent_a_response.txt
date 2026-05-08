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

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx >= dy else dy

    # Greedy step: maximize distance as evader, minimize as pursuer.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny)
            # Small obstacle-nearness penalty to avoid getting wedged.
            near = 0
            for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in blocked:
                    near += 1
            # Tie-break prefers keeping direction toward/away from opponent.
            dir_bias = (dx * (1 if nx >= ox else -1 if nx < ox else 0) +
                         dy * (1 if ny >= oy else -1 if ny < oy else 0))
            if i_am_evader:
                score = d - 0.05 * near + 0.001 * dir_bias
                moves.append((score, dx, dy))
            else:
                score = -d - 0.05 * near + 0.001 * dir_bias
                moves.append((score, dx, dy))

    if not moves:
        return [0, 0]

    # Deterministic tie-break: highest/lowest score then lexicographic (dx,dy).
    moves.sort(key=lambda t: (t[0], -t[1], -t[2]) if i_am_evader else (t[0], -t[1], -t[2]), reverse=True)
    _, dx, dy = moves[0]
    return [int(dx), int(dy)]