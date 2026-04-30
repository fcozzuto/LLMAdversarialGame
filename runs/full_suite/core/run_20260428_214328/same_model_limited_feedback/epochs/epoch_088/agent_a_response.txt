def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # If no resources, just move toward center while staying away from obstacles and opponent.
    if not resources:
        tx, ty = (w-1)/2.0, (h-1)/2.0
        best = None
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx+dx, sy+dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                v = -10**9
            else:
                v = -dist((nx, ny), (tx, ty)) + 0.15 * dist((nx, ny), (ox, oy))
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    # Choose a target resource where we can gain the most (self closer than opponent), else intercept the opponent's nearest.
    best_r = None
    best_gain = -10**18
    for r in resources:
        d_s = dist((sx, sy), r)
        d_o = dist((ox, oy), r)
        gain = d_o - d_s
        if gain > best_gain:
            best_gain, best_r = gain, r

    # If we aren't ahead on any resource, switch to intercept: pick resource minimizing opponent distance.
    if best_gain <= 0:
        best_r = min(resources, key=lambda r: (dist((ox, oy), r), dist((sx, sy), r), r[0], r[1]))

    target = best_r
    cur_ds = dist((sx, sy), target)
    cur_do = dist((ox, oy), target)

    # Evaluate all moves deterministically.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            v = -10**12
        else:
            ns = (nx, ny)
            ds = dist(ns, target)
            do = dist((ox, oy), target)
            # Encourage reducing our distance to target and worsening opponent's distance to it.
            v = (cur_do - do) * 3.0 + (cur_ds - ds) * 2.0
            # Prefer moves that keep us away from opponent when contested.
            v += 0.12 * dist(ns, (ox, oy))
            # Avoid getting trapped behind obstacles roughly by discouraging adjacency to obstacles.
            adj_obs = 0
            for adx, ady in deltas:
                ax, ay = nx+adx, ny+ady
                if in_bounds(ax, ay) and (ax, ay) in obstacles:
                    adj_obs += 1
            v -= 0.06 * adj_obs
            # Tiny tie-breaker toward progressing toward the target.
            v += -0.001 * (abs(nx - target[0]) + abs(ny - target[1]))
        if v > bestv:
            bestv, best = v, [dx, dy]
    return best