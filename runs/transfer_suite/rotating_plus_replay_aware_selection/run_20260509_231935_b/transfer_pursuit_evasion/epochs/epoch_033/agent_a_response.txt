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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def min_obst_manh(x, y):
        if not obs:
            return 99
        best = 99
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
        return best

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    ocx, ocy = ox, oy
    best_corner = corners[0]
    best_cd = 10**9
    for cx, cy in corners:
        d = dist2(ox, oy, cx, cy)
        if d < best_cd:
            best_cd = d
            best_corner = (cx, cy)
    tcx, tcy = best_corner

    best_val = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        d2 = dist2(nx, ny, ox, oy)
        obst = min_obst_manh(nx, ny)  # larger is better (further from obstacles)
        to_corner = dist2(nx, ny, tcx, tcy)

        if is_evader:
            # maximize distance to pursuer, also move away from its corner target
            val = d2 * 10 + obst - to_corner * 0.1
        else:
            # minimize distance to evader, but keep some obstacle clearance; also drift evader toward its corner
            val = -d2 * 10 + obst + to_corner * 0.05

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]