def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    is_evader = ("evad" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def nearest_obst_dist(x, y):
        if not obs:
            return 99
        best = 99
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
        return best

    if is_evader:
        # Run to farthest corner from pursuer, while increasing distance to pursuer.
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        best_move, best_val = (0, 0), -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs:
                continue
            v = dist2(nx, ny, ox, oy) + 0.7 * dist2(nx, ny, tx, ty)
            v -= 0.8 / max(1, nearest_obst_dist(nx, ny))
            if v > best_val:
                best_val, best_move = v, (dx, dy)
        return [best_move[0], best_move[1]]

    # Pursuer: minimize distance to evader/opponent; also bias toward locking into nearer corner to the opponent.
    tx, ty = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    best_move, best_val = (0, 0), -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        d = dist2(nx, ny, ox, oy)
        v = -d + 0.25 * (-dist2(nx, ny, tx, ty))
        v -= 0.6 / max(1, nearest_obst_dist(nx, ny))
        # slight preference to avoid staying if equivalent
        v -= 0.001 * (1 if (dx == 0 and dy == 0) else 0)
        if v > best_val:
            best_val, best_move = v, (dx, dy)
    return [best_move[0], best_move[1]]