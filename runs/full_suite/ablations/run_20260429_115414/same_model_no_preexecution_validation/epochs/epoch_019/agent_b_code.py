def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def obs_dist(x, y):
        if not obs_set: return 99
        md = 99
        for px, py in obs_set:
            d = cheb(x, y, px, py)
            if d < md: md = d
        return md
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = w // 2, h // 2
        best = (float("-inf"), 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            score = (cheb(ox, oy, nx, ny) - cheb(ox, oy, sx, sy)) + (cheb(nx, ny, cx, cy) - cheb(sx, sy, cx, cy)) * -0.3
            od = obs_dist(nx, ny)
            score -= 0.8 * (1.0 / (od + 1e-9)) if od <= 2 else 0
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best_score, best_dx, best_dy = float("-inf"), 0, 0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        od = obs_dist(nx, ny)
        obs_pen = 1.6 if od <= 1 else (0.9 if od == 2 else 0.0)
        # Choose the resource that benefits us most from this candidate cell.
        local_best = float("-inf")
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive => we are closer to this resource
            val = 12.0 * lead - 0.55 * ds + 0.15 * cheb(nx, ny, ox, oy)
            local_best = val if val > local_best else local_best
        score = local_best - obs_pen
        # Small deterministic tie-break: prefer moves with smaller ds to nearest resource.
        if score > best_score + 1e-9:
            best_score, best_dx, best_dy = score, dx, dy
        elif abs(score - best_score) <= 1e-9:
            # Tie-break by closer to best resource among remaining; use first in fixed order.
            # Compute once more: nearest distance from