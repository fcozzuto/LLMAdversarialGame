def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    self_role = observation.get("self_role", "pursuer")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(x1, y1, x2, y2):
        # Chebyshev approximates movement with diagonals
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx >= dy else dy

    def free_neighbors(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (dx == 0 and dy == 0) or (not inb(nx, ny)) or (nx, ny) in obs_set:
                    continue
                cnt += 1
        return cnt

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if self_role == "pursuer":
        best_score = -10**18
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                nx, ny = sx, sy
            dist = d(nx, ny, ox, oy)
            # Prefer tighter pursuit; slight tie-break for mobility
            neigh = free_neighbors(nx, ny)
            obs_pen = 0
            for ax, ay in obs_set:
                ad = abs(ax - nx) + abs(ay - ny)
                if ad <= 1:
                    obs_pen += 2
                elif ad <= 2:
                    obs_pen += 1
            score = (-1000 * dist) + (3 * neigh) - obs_pen
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # evader: maximize distance from pursuer and keep mobility, bias to corners away from opponent
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far = max(corners, key=lambda c: d(c[0], c[1], ox, oy))

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy
        dist_away = d(nx, ny, ox, oy)
        dist_corner = d(nx, ny, far[0], far[1])
        neigh = free_neighbors(nx, ny)
        obs_pen = 0
        for ax, ay in obs_set:
            ad = abs(ax - nx) + abs(ay - ny)
            if ad <= 1:
                obs_pen += 2
            elif ad <= 2:
                obs_pen += 1
        # First maximize escape from opponent; then drift toward far corner; keep mobility
        score = (1200 * dist_away) + (2 * dist_corner) + (6 * neigh) - obs_pen
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]