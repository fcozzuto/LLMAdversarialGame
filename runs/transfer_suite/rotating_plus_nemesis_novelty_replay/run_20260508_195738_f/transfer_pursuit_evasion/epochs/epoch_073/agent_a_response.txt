def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def nearest_corner_dist(x, y):
        return min(md(x, y, cx, cy) for cx, cy in corners)

    target_corner = max(corners, key=lambda c: md(ox, oy, c[0], c[1]))

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        dist = md(nx, ny, ox, oy)
        corner_dist = md(nx, ny, target_corner[0], target_corner[1])
        opp_corner_dist = nearest_corner_dist(ox, oy)

        if self_is_evader:
            # Maximize separation; also drift toward a corner farthest from pursuer.
            val = (dist * 1000) + (corner_dist) - (nearest_corner_dist(nx, ny)) - (opp_corner_dist * 0)
            better = best_val is None or val > best_val
        else:
            # Minimize separation; slight bias toward reducing corner distance to close lanes.
            val = (-dist * 1000) - (nearest_corner_dist(nx, ny)) + (corner_dist * 0)
            better = best_val is None or val > best_val

        if better:
            best_val = val
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]