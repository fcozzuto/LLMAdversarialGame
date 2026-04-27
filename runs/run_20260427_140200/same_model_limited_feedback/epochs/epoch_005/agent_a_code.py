def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    if not resources:
        tx, ty = (w-1)/2.0, (h-1)/2.0
        best = None
        bestk = None
        for dx, dy in deltas:
            nx, ny = sx+dx, sy+dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            k = (dist((nx, ny), (tx, ty)), abs(nx-tx)+abs(ny-ty))
            if best is None or k < bestk:
                bestk, best = k, [dx, dy]
        return best if best is not None else [0, 0]
    best = [0, 0]
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((nx, ny), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            if ds == 0:
                score = -1e6
            else:
                # Prefer resources we can reach much sooner than opponent.
                score = (ds - do) * 100.0 + ds * 1.0 - (do == 0) * 200.0
                # If opponent is at most as close, slightly avoid.
                if do <= ds:
                    score += 50.0
                # If we are stuck near obstacle, mild penalty
                for adx, ady in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ax, ay = nx+adx, ny+ady
                    if inb(ax, ay) and (ax, ay) in obstacles:
                        score += 0.6
                        break
            if score < v:
                v = score
        if bestv is None or v < bestv:
            bestv, best = v, [dx, dy]
    return best