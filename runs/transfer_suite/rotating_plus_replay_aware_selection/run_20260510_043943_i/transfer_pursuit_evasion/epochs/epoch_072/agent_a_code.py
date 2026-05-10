def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or (("evader" in opp_role) and ("pursuer" not in self_role))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        d1 = abs(x1 - x2)
        d2 = abs(y1 - y2)
        return d1 if d1 > d2 else d2

    # Simulate opponent as pursuer (minimize Chebyshev distance)
    def opp_move(px, py, tx, ty):
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not in_bounds(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, dx, dy)
        return best[1], best[2]

    best_move = (0, 0)
    if is_evader:
        # 2-ply: choose move that maximizes distance after opponent "pursuer" response.
        best_val = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            adx, ady = opp_move(ox, oy, nx, ny)
            nax, nay = ox + adx, oy + ady
            val = cheb(nx, ny, nax, nay)
            # small deterministic tie-break: prefer moves that increase Manhattan to farthest corner
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            fc = max(corners, key=lambda c: abs(c[0] - nax) + abs(c[1] - nay))
            val = val * 100 + (abs(fc[0] - nx) + abs(fc[1] - ny))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # Pursuer: 1-step minimize distance; if tie, avoid obstacles already handled; deterministic tie-break toward opponent.
        best_d = 10**9
        best_s = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d < best_d:
                best_d = d
                best_move = (dx, dy)
            elif d == best_d:
                # tie-break: prefer reducing manhattan and moving toward opponent
                m = abs(nx - ox) + abs(ny - oy)
                s = (-(m * 10 + cheb(nx, ny, ox, oy)), dx, dy)
                if s > best_s:
                    best_s = s
                    best_move = (dx, dy)

    dx, dy = int(best_move[0]), int(best_move[1])
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]