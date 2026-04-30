def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if not p or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set

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

    def neighbor_candidates():
        cand = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                cand.append((dx, dy, nx, ny))
        if not cand:
            return [(0, 0, sx, sy)]
        return cand

    cand = neighbor_candidates()
    # If resources exist: maximize advantage over opponent for a reachable resource,
    # then slightly prefer safety (distance from obstacles) and staying closer to center.
    if resources:
        cx, cy = w // 2, h // 2
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in cand:
            safety = obs_dist(nx, ny)
            # If in/adjacent to obstacle, heavily reduce
            safety_pen = 0.0 if safety >= 2 else (5 - 1.7 * safety)
            center = cheb(nx, ny, cx, cy)
            # Pick the resource that gives largest immediate advantage after this move
            best_adv = -10**18
            for r in resources:
                rx, ry = int(r[0]), int(r[1])
                if not inb(rx, ry): 
                    continue
                my_t = cheb(nx, ny, rx, ry)
                op_t = cheb(ox, oy, rx, ry)
                # Advantage: positive means we arrive sooner
                adv = (op_t - my_t)
                # Tie-break: prefer resources closer for us (smaller my_t)
                adv -= 0.15 * my_t
                if adv > best_adv:
                    best_adv = adv
            v = best_adv - 0.9 * center - 2.8 * safety_pen
            # Secondary deterministic tie-break: prefer fewer steps overall (small center and fewer my distances implied by best_adv)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No resources: deterministically drift to safer central cell while keeping away from opponent.
    cx, cy = w // 2, h // 2
    best = (0, 0); bestv = 10**18
    for dx, dy, nx, ny in cand:
        safety = obs_dist(nx, ny)
        # Prefer max safety first, then closer to center, then farther from opponent
        v = (-(safety), cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy))
        # Convert tuple comparison deterministically by using a lexicographic minimization strategy
        if v < bestv:
            bestv = v; best = (dx, dy)
    return [int(best[0]), int(best[1])]