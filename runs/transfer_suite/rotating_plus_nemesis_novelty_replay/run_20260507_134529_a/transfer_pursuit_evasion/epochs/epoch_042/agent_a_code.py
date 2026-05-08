def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            if ok(x + dx, y + dy):
                m += 1
        return m

    def nearest_obstacle_d2(x, y):
        best = 10**9
        for ox2, oy2 in obstacles:
            d = dist2(x, y, ox2, oy2)
            if d < best:
                best = d
        return best if best != 10**9 else 10**9

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_opp = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)  # avoid getting trapped near wall runners
        obs_d = nearest_obstacle_d2(nx, ny)
        # Scoring: pursuer minimize distance, maximize freedom; evader do opposite.
        if is_evader:
            score = ( -d_to_opp, -(mob), -obs_d, dx, dy )
            # maximize distance => minimize negative distance
        else:
            score = ( d_to_opp, -(mob), -obs_d, dx, dy )
            # minimize distance
        if best is None or score < best:
            best = score
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move