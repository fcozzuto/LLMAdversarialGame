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

    def corner_bias(x, y):
        # For evader, prefer corners far from opponent; for pursuer, prefer near center-ish.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        if i_am_evader:
            best = None
            for cx, cy in corners:
                d = abs(cx - x) + abs(cy - y)
                if best is None or d < best:
                    best = d
            return best  # larger when closer to some corner? (we minimize negative later)
        else:
            return -(abs(x - (w - 1) / 2) + abs(y - (h - 1) / 2))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny)
        # Evader maximizes distance; pursuer minimizes distance.
        base = d if i_am_evader else -d
        # Small deterministic bias: stay still slightly preferred when tied, then move order.
        prefer = 1 if (dx == 0 and dy == 0) else 0
        bias = corner_bias(nx, ny) * (0.001 if i_am_evader else 0.001)
        score = base * 1000 + prefer + bias
        if best is None or score > best:
            best = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]