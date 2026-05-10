def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    obs_list = list(obs)
    def obstacle_penalty(x, y):
        if not obs_list:
            return 0
        best = 10**9
        for ex, ey in obs_list:
            d2 = dist2(x, y, ex, ey)
            if d2 < best:
                best = d2
        # encourage staying away when close
        if best <= 1:
            return 10000
        if best <= 4:
            return 800
        if best <= 9:
            return 200
        if best <= 16:
            return 60
        return 0

    best = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d2 = dist2(nx, ny, ox, oy)
        pen = obstacle_penalty(nx, ny)
        # also discourage drifting toward walls when evading
        wall_pen = 0
        if nx in (0, w - 1) or ny in (0, h - 1):
            wall_pen = 5 if is_evader else 0
        if is_evader:
            # maximize distance from pursuer
            val = -d2 + pen + wall_pen
            # convert to minimization
        else:
            # minimize distance to pursuer
            val = d2 + pen + wall_pen
        if best is None or val < best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]