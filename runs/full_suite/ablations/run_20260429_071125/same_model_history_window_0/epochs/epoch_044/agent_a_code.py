def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x,y):
        return 0 <= x < w and 0 <= y < h

    def dist(a,b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Choose target resource with opponent-aware advantage
    if resources:
        best = None
        best_val = -10**9
        for r in resources:
            ds = dist((sx, sy), r)
            do = dist((ox, oy), r)
            # Advantage favors resources we're closer to; slight preference for nearer own pickup
            val = (do - ds) * 10 - ds
            # Avoid selecting resources blocked by immediate obstacle from our position
            if (r[0], r[1]) in obstacles:
                val -= 1000
            if val > best_val:
                best_val = val
                best = r
        tx, ty = best
    else:
        # No resources: move to center-ish while keeping distance
        tx, ty = (w//2, h//2)

    # Evaluate moves
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_self_to_target = dist((nx, ny), (tx, ty))
        d_opp_to_target = dist((ox, oy), (tx, ty))

        # If we step closer to target and are not letting opponent be significantly closer
        # Encourage distancing from opponent to reduce contention
        d_to_opp = dist((nx, ny), (ox, oy))

        # Obstacle-aware: penalize moves adjacent to obstacles less than those moving into "tight" spots
        adj_obst = 0
        for ax in (-1,0,1):
            for ay in (-1,0,1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if inb(xx, yy) and (xx, yy) in obstacles:
                    adj_obst += 1

        # Deterministic tie-breaking uses dx,dy order via tuple sorting later
        score = 0
        score -= d_self_to_target * 5
        score += d_to_opp * 1.5
        score += (d_opp_to_target - d_self_to_target) * 2
        score -= adj_obst * 0.3

        # If stepping directly onto a resource square, strongly prefer it
        if resources and (nx, ny) in set(tuple(p) for p in resources):
            score += 10000

        moves.append((score, -d_self_to_target, d_to_opp, -abs(dx), -abs(dy), dx, dy))

    if not moves:
        return [0, 0]

    moves.sort(reverse=True)
    _, _, _, _, _, dx, dy = moves[0]
    return [int(dx), int(dy)]