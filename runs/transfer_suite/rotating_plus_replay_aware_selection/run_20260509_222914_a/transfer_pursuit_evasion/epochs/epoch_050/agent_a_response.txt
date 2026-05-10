def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    dirs = [(-1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1), (0, 0)]
    if w >= 8 and h >= 8:
        dirs = [(1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1), (0, 0)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_score = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, ox, oy)
        # extra tie-break: keep away/toward nearest obstacle slightly
        obs_bonus = 0
        if obstacles:
            min_ad = 999
            for ax, ay in obstacles:
                ad = abs(nx - ax) + abs(ny - ay)
                if ad < min_ad: min_ad = ad
            if min_ad == 0:
                continue
            if is_pursuer:
                obs_bonus = -0.05 * (min_ad == 1) - 0.01 * min_ad
            else:
                obs_bonus = 0.02 * min_ad

        if is_pursuer:
            score = -d + obs_bonus
            better = (best_score is None) or (score > best_score) 
        else:
            score = d + obs_bonus
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best_move = [dx, dy]

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]