def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = []
    for p in obstacles:
        try:
            x, y = p
            obs.append((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    is_evader = ("evad" in sr) or ("escape" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_penalty(x, y):
        if not obs:
            return 0
        # Penalize closeness to obstacles and being on them.
        pen = 0
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d == 0:
                pen += 10000
            else:
                pen += 12.0 / d
        return pen

    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    target_corner = far_corner if is_evader else near_corner

    best_dx, best_dy = 0, 0
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            val = -10**17 if is_evader else 10**17
        else:
            d_opp2 = dist2(nx, ny, ox, oy)
            d_corner2 = dist2(nx, ny, target_corner[0], target_corner[1])
            obs_pen = obstacle_penalty(nx, ny)
            if is_evader:
                val = d_opp2 - 0.15 * d_corner2 - obs_pen
                # If already winning by staying away, slightly prefer moves with larger Manhattan distance.
                man = abs(nx - ox) + abs(ny - oy)
                val += 0.02 * man
                if val > best_val:
                    best_val, best_dx, best_dy = val, dx, dy
            else:
                val = d_opp2 + 0.15 * d_corner2 + obs_pen
                man = abs(nx - ox) + abs(ny - oy)
                val += -0.02 * man
                if val < best_val:
                    best_val, best_dx, best_dy = val, dx, dy

    return [int(best_dx), int(best_dy)]