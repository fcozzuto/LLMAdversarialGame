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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny)
        # Tie-break deterministically: prefer dx,dy ordering and slightly prefer staying still when equal.
        prefer = -1 if (dx == 0 and dy == 0) else 0
        score = (d if i_am_evader else -d) * 10 + prefer
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]