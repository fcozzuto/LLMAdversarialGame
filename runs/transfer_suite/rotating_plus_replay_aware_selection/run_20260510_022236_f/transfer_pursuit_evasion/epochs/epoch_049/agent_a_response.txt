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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def min_obs_dist(x, y):
        if not obs:
            return 99
        m = 10**9
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < m:
                m = d
        return m

    # Evader: head to farthest corner; Pursuer: head to nearest corner / chase directly.
    best_corner = None
    if is_evader:
        best_corner = max(corners, key=lambda t: dist(t[0], t[1], ox, oy))
    else:
        best_corner = min(corners, key=lambda t: dist(t[0], t[1], ox, oy))

    best_move = [0, 0]
    best_score = -10**18 if is_evader else 10**18

    # Deterministic tie-break order by fixed delta list; evaluate all.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d_opp = dist(nx, ny, ox, oy)
        d_corner = dist(nx, ny, best_corner[0], best_corner[1])
        mo = min_obs_dist(nx, ny)

        # Obstacle penalty: stronger if too close
        if mo <= 0:
            obs_pen = -10**6
        elif mo == 1:
            obs_pen = -200
        elif mo == 2:
            obs_pen = -40
        elif mo == 3:
            obs_pen = -12
        else:
            obs_pen = 0

        if is_evader:
            # Prefer maximizing distance from pursuer and cornering, while avoiding obstacles.
            score = (d_opp * 3) + (-d_corner) + obs_pen
            better = score > best_score
        else:
            # Prefer minimizing distance to pursuer and reducing corner distance slightly.
            score = (d_opp * -3) + (-d_corner // 2) + obs_pen
            better = score > best_score

        if better:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]