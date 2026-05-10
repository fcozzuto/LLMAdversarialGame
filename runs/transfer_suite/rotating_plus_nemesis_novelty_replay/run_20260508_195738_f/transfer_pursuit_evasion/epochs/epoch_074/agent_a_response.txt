def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    # Heuristic role inference: pursuer tries to minimize distance, evader maximize.
    self_is_pursuer = ("purs" in self_role) or (("evad" in opp_role) and ("agent" in self_role or "purs" in self_role or "purs" in opp_role))

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

    def best_corner_score(x, y):
        # For evader: prefer farthest corner from opponent; for pursuer: prefer nearest.
        dmin = min(md(x, y, cx, cy) for cx, cy in corners)
        dmax = max(md(ox, oy, cx, cy) for cx, cy in corners)
        return (dmin, dmax)

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        dist = md(nx, ny, ox, oy)
        # Obstacle proximity penalty: avoid moving adjacent to obstacles if possible.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj += 1

        if self_is_pursuer:
            # Minimize distance to opponent; slightly bias toward corners that are likely to force capture.
            corner_bias = min(md(nx, ny, cx, cy) for cx, cy in corners)
            val = dist * 10 + adj * 2 + corner_bias
            better = (best_val is None) or (val < best_val)
        else:
            # Maximize distance; if tied, move to farthest-from-opponent corner.
            corner_farthest = max(md(nx, ny, cx, cy) for cx, cy in corners)
            val = (-dist) * 10 + (-corner_farthest) + adj * 2  # larger dist/corner gives smaller val
            better = (best_val is None) or (val < best_val)

        if better:
            best_val = val
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]