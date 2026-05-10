def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role) or ("evasion" in str(observation.get("environment_name", "")).lower())

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if is_evader:
        tx, ty = max(corners, key=lambda c: dist2(sx, sy, c[0], c[1]))
    else:
        tx, ty = ox, oy

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_t = dist2(nx, ny, tx, ty)
        # Wall-run bias: prefer staying near edges when evading; prefer moving off edges when pursuing.
        edge_pen = (0 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 1) if is_evader else (0 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 1)
        # Obstacle proximity: avoid stepping near obstacles.
        obs_near = 0
        for (ax, ay) in blocked:
            if abs(nx - ax) <= 1 and abs(ny - ay) <= 1:
                obs_near += 1
        # Score: evader maximize distance to pursuer + corner direction; pursuer minimize distance to evader.
        if is_evader:
            v = d_opp * 10 + d_t - obs_near * 40 + edge_pen * 5
        else:
            v = -d_opp * 10 - d_t - obs_near * 40 - edge_pen * 5
        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]