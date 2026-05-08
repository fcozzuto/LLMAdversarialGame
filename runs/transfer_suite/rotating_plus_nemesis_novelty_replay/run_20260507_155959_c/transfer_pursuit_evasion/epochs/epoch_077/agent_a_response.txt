def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.append((int(x), int(y)))
        except Exception:
            pass
    obs_set = set(obstacles)

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or role == "evader"

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def nearest_obs_dist(x, y):
        if not obstacles:
            return 99
        best = 99
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    # Determine if a move would be blocked; engine keeps agent in place if invalid.
    def candidate_pos(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            return sx, sy
        return nx, ny

    # For pursuer: minimize distance, avoid obstacles, and align by reducing both axes.
    # For evader: maximize distance, avoid obstacles less, and bias toward corners when possible.
    axis_align_bonus = -1  # larger magnitude favors reducing both dx and dy when pursuer
    best_val = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = candidate_pos(dx, dy)
        d = md(nx, ny, ox, oy)
        nd = nearest_obs_dist(nx, ny)

        if is_evader:
            # escape: maximize distance, keep some separation from obstacles, slight wall bias
            wall_bias = min(nx, ny, w - 1 - nx, h - 1 - ny)  # smaller => closer to wall
            # Prefer moving toward walls if it increases escape quality; avoid stepping into obstacles via nd.
            val = d * 10 + (nd) + (-(wall_bias))
        else:
            # chase: minimize distance strongly, then prefer moves that improve axis alignment
            # (reduce abs(x-ox) and abs(y-oy) at same time), while avoiding being trapped near obstacles.
            ax0, ay0 = abs(sx - ox), abs(sy - oy)
            ax1, ay1 = abs(nx - ox), abs(ny - oy)
            improve_both = (1 if (ax1 < ax0 and ay1 < ay0) else 0)
            obstacle_risk = (0 if nd >= 2 else (3 - nd))  # closer than 2 => risk
            val = -d * 100 + improve_both * 25 - obstacle_risk * 10 + axis_align_bonus * (abs(ax1 - ay1))

        if best_val is None or val > best_val:
            best_val = val
            best_move = [int(dx), int(dy)]

    return best_move