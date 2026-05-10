def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("evad" in opponent_role)

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            x = int(x); y = int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.append((x, y))
        except:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # tie-break deterministically: prefer (0,0) then lexicographic by dx,dy
    order = { (0,0): 0, (-1,-1):1, (-1,0):2, (-1,1):3, (0,-1):4, (0,1):5, (1,-1):6, (1,0):7, (1,1):8 }

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def min_obs_dist(nx, ny):
        if not obstacles:
            return 99
        dmin = 99
        for (bx, by) in obstacles:
            d = abs(nx - bx) + abs(ny - by)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    break
        return dmin

    best_dxdy = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        if nx < 0: nx = 0
        if ny < 0: ny = 0
        if nx >= w: nx = w - 1
        if ny >= h: ny = h - 1

        dist = md(nx, ny, ox, oy)
        d_obs = min_obs_dist(nx, ny)

        # pursuer: minimize distance; evader: maximize distance
        if is_pursuer:
            val = -dist
        else:
            val = dist

        # avoid obstacles (more strongly than one-step distance)
        val += 0.8 * d_obs

        # if capture occurs (radius 0), pursuer should immediately take it; evader should avoid it
        if dist == 0:
            val = 10**6 if is_pursuer else -10**6

        tieb = order[(dx, dy)]
        if best_val is None or val > best_val or (val == best_val and tieb < order[best_dxdy]):
            best_val = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]