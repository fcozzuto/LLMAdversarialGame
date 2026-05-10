def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "pursuer")).lower()
    evader = ("evader" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        return abs(ax - bx) if abs(ax - bx) > abs(ay - by) else abs(ay - by)

    def dist_to_nearest_obstacle(nx, ny):
        if not blocked:
            return 999
        best = 999
        for (bx, by) in blocked:
            d = cheb(nx, ny, bx, by)
            if d < best:
                best = d
        return best

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_corner = max(cheb(nx, ny, cx, cy) for (cx, cy) in corners)
        d_obs = dist_to_nearest_obstacle(nx, ny)

        # Obstacle proximity: avoid getting adjacent when possible
        # For d_obs==0 impossible (blocked), for 1-2 heavily penalize.
        obstacle_pen = 0
        if d_obs <= 1:
            obstacle_pen = 50
        elif d_obs == 2:
            obstacle_pen = 15
        elif d_obs == 3:
            obstacle_pen = 6
        elif d_obs == 4:
            obstacle_pen = 3

        # Pursuit/Evasion objective
        if evader:
            val = (-d_opp) + 0.02 * d_corner - 0.3 * obstacle_pen
        else:
            val = (d_opp) - 0.02 * d_corner + 0.3 * obstacle_pen

        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if evader:
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]
            else:
                if val < best_val:
                    best_val = val
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]