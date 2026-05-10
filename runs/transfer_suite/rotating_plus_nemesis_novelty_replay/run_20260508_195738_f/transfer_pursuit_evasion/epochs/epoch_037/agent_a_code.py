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

    role = str(observation.get("self_role", "")).lower()
    is_evader = "evader" in role and "purs" not in role

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def nearest_obs_dist(x, y):
        if not obs:
            return 1000
        dmin = 1000
        for ex, ey in obs:
            d = abs(x - ex) + abs(y - ey)
            if d < dmin:
                dmin = d
        return dmin

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18 if is_evader else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d = manhattan(nx, ny, ox, oy)

        if is_evader:
            corner_target = max(corners, key=lambda c: manhattan(c[0], c[1], ox, oy))
            corner_dist = manhattan(nx, ny, corner_target[0], corner_target[1])
            score = d + 0.35 * corner_dist - 0.25 / (1 + nearest_obs_dist(nx, ny))
            if score > best_score:
                best_score, best_move = score, (dx, dy)
        else:
            corner_target = max(corners, key=lambda c: manhattan(c[0], c[1], ox, oy))
            corner_dist = manhattan(nx, ny, corner_target[0], corner_target[1])
            score = -d - 0.10 * nearest_obs_dist(nx, ny) + 0.05 * corner_dist
            if score < best_score:
                best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]