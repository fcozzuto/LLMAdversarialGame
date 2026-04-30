def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y): return inb(x, y) and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def obstacle_pen(x, y):
        if not obs: return 0.0
        md = 99
        for px, py in obs:
            d = cheb(x, y, px, py)
            if d < md:
                md = d
                if md <= 1: break
        if md <= 0: return 10.0
        if md == 1: return 3.5
        if md == 2: return 1.2
        return 0.0

    # Score candidate move by evaluating best contested resource after move, plus safety vs opponent.
    best_move = (0, 0)
    best_val = -10**18
    has_res = bool(resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        opp_d = cheb(nx, ny, ox, oy)
        safe = opp_d * 0.35  # prefer being farther from opponent

        if not has_res:
            # Move towards center while avoiding obstacles
            cx, cy = (w - 1) // 2, (h - 1) // 2
            distc = cheb(nx, ny, cx, cy)
            val = safe + (-0.22 * distc) - obstacle_pen(nx, ny)
        else:
            # Choose a resource; prioritize ones where we're not behind (self_dist <= opp_dist) and closer.
            target_score = -10**18
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # If opponent is already closer to that resource than we would be, reduce its attractiveness.
                contest = 0.0
                if sd > od: contest = -(sd - od) * 0.9
                # Also prefer resources that are actually close.
                s = -sd * 1.15 + contest
                # Slightly prefer resources closer to our current position to avoid "teleport" detours.
                s += -cheb(sx, sy, rx, ry) * 0.12
                if s > target_score:
                    target_score = s
            val = safe + target_score - obstacle_pen(nx, ny)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]