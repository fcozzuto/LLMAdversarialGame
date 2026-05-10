def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.append((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    def obstacle_term(x, y):
        if not obs:
            return 0
        best = 10**9
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        if best == 0:
            return -10**7
        if best == 1:
            return -50
        if best == 2:
            return -12
        return 0

    def nearest_corner(px, py):
        return min(corners, key=lambda c: abs(c[0] - px) + abs(c[1] - py))

    target_corner = nearest_corner(ox, oy)  # evader's likely corner (closest to them)
    tx, ty = target_corner

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy  # engine would keep still; keep deterministic
        dist = abs(nx - ox) + abs(ny - oy)
        corner_dist = abs(nx - tx) + abs(ny - ty)
        wdist = wall_dist(nx, ny)
        oterm = obstacle_term(nx, ny)

        # pursuer: minimize distance, also get into evader's corner lane
        if not is_evader:
            score = -dist * 20 - corner_dist * 3 + wdist * 1 + oterm
        else:
            # evader: maximize distance and increase distance from pursuer's best corner pressure
            pursuer_corner = nearest_corner(sx, sy)
            pcx, pcy = pursuer_corner
            pressure = abs(nx - pcx) + abs(ny - pcy)
            score = dist * 22 + corner_dist * 2 - pressure * 1 + wdist * 0.5 + oterm

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]