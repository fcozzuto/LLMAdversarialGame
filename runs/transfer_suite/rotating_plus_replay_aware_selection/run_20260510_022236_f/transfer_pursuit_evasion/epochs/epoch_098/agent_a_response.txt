def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def obstacle_pen(x, y):
        if not obstacles:
            return 0
        dmin = 10**9
        for px, py in obstacles:
            d = abs(px - x) + abs(py - y)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    break
        if dmin == 0:
            return 10**6
        if dmin == 1:
            return 60
        if dmin == 2:
            return 26
        if dmin == 3:
            return 12
        return 0

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = max(abs(ox - nx), abs(oy - ny))
        pen = obstacle_pen(nx, ny)
        if is_evader:
            score = dist * 20 - pen - (abs((nx + ny) - (ox + oy)) * 2)
        else:
            score = -dist * 20 - pen - (abs((nx + ny) - (ox + oy)) * 2)
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best