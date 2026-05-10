def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("purs" in opponent_role) or ("escape" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Prefer moving toward a corner that best separates (evader) or closes (pursuer) distance to opponent.
    best_corner = corners[0]
    if self_is_evader:
        best_corner_val = -1
        for c in corners:
            d = md(c[0], c[1], ox, oy)
            if d > best_corner_val:
                best_corner_val = d
                best_corner = c
    else:
        best_corner_val = 10**9
        for c in corners:
            d = md(c[0], c[1], ox, oy)
            if d < best_corner_val:
                best_corner_val = d
                best_corner = c

    # If we can capture immediately (pursuer) at capture radius 0.
    if not self_is_evader:
        dx0 = ox - sx
        dy0 = oy - sy
        if dx0 in (-1, 0, 1) and dy0 in (-1, 0, 1) and (sx + dx0, sy + dy0) not in obstacles:
            return [int(dx0), int(dy0)]

    obs_list = list(obstacles)

    def nearest_obs_dist(x, y):
        if not obs_list:
            return 99
        dmin = 99
        for bx, by in obs_list:
            d = abs(x - bx) + abs(y - by)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    break
        return dmin

    # Score: main objective is distance to opponent, secondary is toward chosen corner, tertiary avoids obstacles.
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_opp = md(nx, ny, ox, oy)
        d_corner = md(nx, ny, best_corner[0], best_corner[1])
        d_obs = nearest_obs_dist(nx, ny)

        # Higher is better after normalization.
        if self_is_evader:
            val = (d_opp * 10) + (-d_corner) + (d_obs)
        else:
            val = (-d_opp * 10) + (-d_corner) + (d_obs)

        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return best_move