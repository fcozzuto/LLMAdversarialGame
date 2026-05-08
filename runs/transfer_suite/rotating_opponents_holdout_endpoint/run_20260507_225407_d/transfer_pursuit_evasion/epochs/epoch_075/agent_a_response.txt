def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    blocked = lambda x, y: (x, y) in obstacles or not inb(x, y)
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in role) or ("hunter" in role) or ("seeker" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        d_to_opp = cheb(nx, ny, ox, oy)

        # Obstacle proximity penalty (moves that hug obstacles are risky in pursuit/evasion).
        min_obs = 10**9
        for (ax, ay) in obstacles:
            t = cheb(nx, ny, ax, ay)
            if t < min_obs:
                min_obs = t
        obs_pen = 0
        if min_obs == 0:
            obs_pen = 1000
        elif min_obs == 1:
            obs_pen = 4
        elif min_obs == 2:
            obs_pen = 2

        # Corner bias: evader runs to farthest corner; pursuer breaks toward nearest corner to tighten routes.
        corner_dist = max(cheb(nx, ny, cx, cy) for (cx, cy) in corners)

        if pursuer:
            primary = -d_to_opp  # minimize distance
            # discourage moving away from nearest corner (greedy tightening)
            nearest_corner = min(cheb(nx, ny, cx, cy) for (cx, cy) in corners)
            key = (primary, -nearest_corner, -obs_pen, -(nx + ny), dx, dy)
        else:
            primary = d_to_opp  # maximize distance
            # prefer cornering while not hugging obstacles
            key = (primary, corner_dist, -obs_pen, (nx + ny) % 2, dx, dy)

        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]