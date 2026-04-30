def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Simple deterministic heuristic:
    # 1) Move towards the nearest resource not blocked by obstacle.
    # 2) If opponent closer to that resource, prefer another safe resource or hold.
    # 3) If no resources available or all blocked, move toward center to gain future access.

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best = None
    best_r = None
    if resources:
        # pick nearest resource
        best_r = min(resources, key=lambda r: dist((sx, sy), r))
        # if opponent closer to that resource, consider other options
        opp_to_r = dist((ox, oy), best_r)
        my_to_r = dist((sx, sy), best_r)
        if opp_to_r < my_to_r:
            # try alternate resource if exists
            alt = [r for r in resources if r != best_r]
            if alt:
                best_r = min(alt, key=lambda r: dist((sx, sy), r))
        # choose move that decreases distance to best_r
        tdx = best_r[0] - sx
        tdy = best_r[1] - sy
        # choose a legal move that best aligns with target
        best = (0,0)
        best_score = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            score = -abs(best_r[0]-nx) - abs(best_r[1]-ny)
            # secondary: favor not stepping onto opponent
            if (nx, ny) == (ox, oy):
                score -= 5
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources; move toward center to improve future reach
    center = (w//2, h//2)
    best = (0,0)
    best_score = -10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = -abs(nx - center[0]) - abs(ny - center[1])
        if (nx, ny) == (ox, oy):
            score -= 5
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]