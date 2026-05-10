def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("evad" in opp_role and "evad" not in self_role)

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.append((x, y))
        except Exception:
            pass

    def cheb2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def obst_pen(nx, ny):
        if not obstacles:
            return 0
        best = 10**18
        for bx, by in obstacles:
            dd = (nx - bx) * (nx - bx) + (ny - by) * (ny - by)
            if dd < best:
                best = dd
        if best == 0:
            return 10**9
        return best  # smaller is worse

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        dist2 = cheb2(nx, ny, ox, oy)
        p = obst_pen(nx, ny)
        if is_pursuer:
            score = -dist2 - (0 if p >= 10**18 else (10**4 / (p + 1)))
        else:
            score = dist2 - (0 if p >= 10**18 else (10**4 / (p + 1)))
            # Stronger corner-chase bias for evader:
            score += -abs((w - 1) - ox) - abs((h - 1) - oy) if (ox + oy) <= ((w - 1) + (h - 1)) else 0

        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]