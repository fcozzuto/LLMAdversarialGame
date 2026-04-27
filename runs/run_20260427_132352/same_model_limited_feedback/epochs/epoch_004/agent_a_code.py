def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def clamp(x, a, b):
        return a if x < a else b if x > b else x
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    free = lambda x,y: (0 <= x < w and 0 <= y < h and (x,y) not in obstacles)
    best = None
    best_score = -10**9
    # Choose a target resource where we are competitive (or at least closest with positive "swing")
    target = None
    if resources:
        best_gain = -10**9
        best_d = 10**9
        for rx, ry in resources:
            d1 = abs(rx - sx) + abs(ry - sy)
            d2 = abs(rx - ox) + abs(ry - oy)
            gain = d2 - d1  # positive means we can reach sooner
            # prioritize: biggest gain, then smaller own distance
            if gain > best_gain or (gain == best_gain and d1 < best_d):
                best_gain = gain
                best_d = d1
                target = (rx, ry)
    if target is None:
        target = (w//2, h//2)
    # Evaluate moves: move toward target while keeping distance from opponent and avoiding obstacles
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, w-1), clamp(sy + dy, 0, h-1)
        if (nx, ny) != (sx + dx, sy + dy) and (nx, ny) in obstacles:
            continue
        if not free(nx, ny):
            continue
        d_to = abs(target[0]-nx) + abs(target[1]-ny)
        d_opp = abs(ox-nx) + abs(oy-ny)
        # obstacle proximity penalty (encourage paths through open space)
        obs_near = 0
        for ax in (-1,0,1):
            for ay in (-1,0,1):
                if (nx+ax, ny+ay) in obstacles:
                    obs_near += 1
        score = (-1.5 * d_to) + (0.8 * d_opp) - (0.4 * obs_near)
        # If opponent is very close, try to increase separation more strongly
        if d_opp <= 2:
            score += 2.0 * d_opp
        # Small tie-breaker: prefer staying inside bounds without "corner hugging"
        score += -0.01 * (abs(nx - (w//2)) + abs(ny - (h//2)))
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best