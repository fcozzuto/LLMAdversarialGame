def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if (sx, sy) == (ox, oy):
        return [0, 0]

    def dist_cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def obstacle_proximity(x, y):
        if not obstacles:
            return 0
        dmin = 10**9
        for px, py in obstacles:
            d = abs(px - x) + abs(py - y)
            if d < dmin:
                dmin = d
        return dmin

    # For evader: aim to maximize distance, and drift toward the corner farthest from pursuer.
    if is_evader:
        tx = (0 if ox >= w / 2 else w - 1)
        ty = (0 if oy >= h / 2 else h - 1)
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d_opp = dist_cheb(nx, ny)
        d_tar = max(abs(tx - nx), abs(ty - ny))
        d_obs = obstacle_proximity(nx, ny)

        if is_evader:
            # maximize distance to opponent; break ties by moving away from obstacles and toward target corner
            score = (d_opp * 1000) + (d_obs * 10) - (d_tar)
        else:
            # minimize distance to opponent; break ties by avoiding obstacles (keep some clearance) and reducing distance to opponent
            score = (-d_opp * 1000) + (d_obs * 2) - (max(abs(ox - nx), abs(oy - ny)) // 1)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]