def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def free_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    def obstacle_penalty(x, y):
        # Strongly avoid being on an obstacle; otherwise slightly steer away.
        if (x, y) in blocked:
            return 10**9
        p = 0
        for bx, by in blocked:
            d = dist2(x, y, bx, by)
            if d == 0:
                return 10**9
            if d <= 4:
                p += (5 - d) * 10
        return p

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy  # engine keeps us in place if invalid

        d2 = dist2(nx, ny, ox, oy)
        obs = obstacle_penalty(nx, ny)

        # Edge preference: for evader go to farthest edge; for pursuer go toward center-ish by minimizing edge distance.
        edge_dist = min(nx, ny, w - 1 - nx, h - 1 - ny)

        if is_evader:
            primary = d2
            score = (primary, -obs, free_count(nx, ny), edge_dist)
            # maximize distance, avoid obstacles, prefer more mobility, and push toward edges (larger edge_dist is better for evader)
        else:
            primary = -d2
            score = (primary, -obs, free_count(nx, ny), -edge_dist)
            # minimize distance, avoid obstacles, prefer mobility, and avoid edges (keep chase tight)

        if best is None or score > best[0]:
            best = (score, [dx, dy])

    return best[1]