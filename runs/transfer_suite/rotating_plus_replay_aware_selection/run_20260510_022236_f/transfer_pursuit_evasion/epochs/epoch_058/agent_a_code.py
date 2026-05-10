def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        target = max(corners, key=lambda c: dist(c[0], c[1], ox, oy))
    else:
        target = (ox, oy)

    def obs_pen(x, y):
        if not obs:
            return 0
        best = 10**9
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
                if best == 0:
                    return 10**6
        if best == 0:
            return 10**6
        if best == 1:
            return 120
        if best == 2:
            return 40
        if best == 3:
            return 15
        return 0

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        d_to_target = dist(nx, ny, target[0], target[1])
        d_to_opp = dist(nx, ny, ox, oy)

        if is_evader:
            # maximize distance from pursuer; keep moving toward far corner while avoiding obstacles
            score = (d_to_opp * 10) - d_to_target - obs_pen(nx, ny)
            # small bias to keep heading consistent: prefer reducing distance to target even if evading
            score += (d_to_target == 0) * 2
        else:
            # minimize distance to evader; avoid obstacles
            score = (-d_to_opp * 12) - obs_pen(nx, ny) - (d_to_target)

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]