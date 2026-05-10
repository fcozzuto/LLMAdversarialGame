def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = []
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.append((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def obst_score(nx, ny):
        # Higher is better (for safety).
        if not obstacles:
            return 0.0
        dmin = 10**9
        for x, y in obstacles:
            d = abs(nx - x) + abs(ny - y)
            if d < dmin:
                dmin = d
        if dmin == 0:
            return -1e6
        if dmin == 1:
            return -200.0
        if dmin == 2:
            return -30.0
        return float(min(dmin, 6)) * 3.0

    # If evading: bias toward corners far from opponent to reduce chase flexibility.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = corners[0]
    best_corner_dist = -1
    for cx, cy in corners:
        d = abs(cx - ox) + abs(cy - oy)
        if d > best_corner_dist:
            best_corner_dist = d
            best_corner = (cx, cy)

    bx, by = best_corner

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)

        dist = abs(nx - ox) + abs(ny - oy)
        safe = obst_score(nx, ny)

        if pursuer:
            # Maximize: safety + strong preference to reduce distance.
            val = (-dist * 100.0) + safe + (-(abs(nx - sx) + abs(ny - sy)) * 0.5)
        else:
            # Maximize: keep distance; also drift toward farthest corner from pursuer.
            corner_dist = abs(nx - bx) + abs(ny - by)
            val = (dist * 120.0) + corner_dist * 6.0 + safe

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]