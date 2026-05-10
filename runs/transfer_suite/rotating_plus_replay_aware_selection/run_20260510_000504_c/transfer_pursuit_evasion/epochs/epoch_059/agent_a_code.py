def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("escape" in self_role) or ("purs" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_obstacle_dist(x, y):
        best = 10**9
        for (bx, by) in obstacles:
            d = md(x, y, bx, by)
            if d < best:
                best = d
                if best <= 0:
                    return 0
        return best if obstacles else 5

    best_move = [0, 0]
    best_val = -10**18 if self_is_evader else 10**18

    far_corner_dist = max(md(sx, sy, cx, cy) for (cx, cy) in corners)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        dist = md(nx, ny, ox, oy)

        corner_dist = max(md(nx, ny, cx, cy) for (cx, cy) in corners)
        center_dist = md(nx, ny, (w - 1) // 2, (h - 1) // 2)
        nobs = nearest_obstacle_dist(nx, ny)

        # Evader: maximize distance, hug far corner, avoid obstacles, prefer staying less "central" against pursuit.
        # Pursuer: minimize distance, prefer moving diagonally toward opponent, avoid stepping into/near obstacles.
        if self_is_evader:
            val = dist * 1000 + corner_dist * 50 + nobs * 20 - center_dist
            # small preference to keep a non-decreasing distance if possible
            if dist >= md(sx, sy, ox, oy):
                val += 25
        else:
            val = -dist * 1000 - nobs * 20 + center_dist
            # favor moves that reduce both coordinates' Manhattan components
            prev = md(sx, sy, ox, oy)
            if dist < prev:
                val -= 30

        if (self_is_evader and val > best_val) or ((not self_is_evader) and val < best_val):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]