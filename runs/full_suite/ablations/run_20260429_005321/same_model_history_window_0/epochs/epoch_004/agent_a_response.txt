def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): 
        dx = abs(a[0]-b[0]); dy = abs(a[1]-b[1])
        return dx + dy
    def best_value(nx, ny):
        if (nx, ny) in obstacles: return -10**9
        if not inb(nx, ny): return -10**9
        if not resources:
            # drift to nearest corner toward opponent to contest space
            tx, ty = (w-1, h-1) if (sx + sy) < (ox + oy) else (0, 0)
            return -dist((nx, ny), (tx, ty)) - 0.1*(abs(nx-w//2)+abs(ny-h//2))
        # Evaluate by comparing our access vs opponent access to each resource
        # Also add a small preference for keeping some distance from obstacles.
        min_score = -10**9
        for rx, ry in resources:
            our_d = dist((nx, ny), (rx, ry))
            opp_d = dist((ox, oy), (rx, ry))
            # winning intent: go for resources where we are closer than opponent
            # tie-breaker: smaller our distance
            score = (opp_d - our_d) * 10 - our_d
            if score > min_score: min_score = score
        # obstacle repulsion (soft)
        adj = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                if (nx+dx, ny+dy) in obstacles: adj += 1
        return min_score - 0.75 * adj

    best = None
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        v = best_value(nx, ny)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy) if best is None else best
            best = (dx, dy)
    return [best[0], best[1]]