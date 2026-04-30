def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def clamp(px, py):
        if px < 0: px = 0
        elif px >= w: px = w - 1
        if py < 0: py = 0
        elif py >= h: py = h - 1
        return px, py

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Pick a target resource we can get relatively sooner than opponent
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds - do, ds, -((rx + ry) % 3), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    # Evaluate candidate next moves
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        # If we're stepping onto a resource, prefer it strongly
        on_res = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0

        nds = dist((nx, ny), (tx, ty))
        ndo = dist((ox, oy), (tx, ty))
        adv = nds - ndo  # smaller is better (we get closer relative to opponent)

        # Obstacle/edge pressure: penalize moves that reduce available space locally
        local_free = 0
        for ex, ey in [(nx-1,ny),(nx+1,ny),(nx,ny-1),(nx,ny+1),(nx-1,ny-1),(nx+1,ny-1),(nx-1,ny+1),(nx+1,ny+1)]:
            ex, ey = clamp(ex, ey)
            if (ex, ey) not in obstacles:
                local_free += 1
        edge_pen = -((nx == 0 or nx == w-1) + (ny == 0 or ny == h-1))  # avoid getting stuck

        score = (-1000 * on_res) + (adv * 10) + (nds) + (-local_free * 0.3) + (edge_pen)
        # Deterministic tie-break by fixed order of deltas
        tie = (best_score is not None and score == best_score and (dx, dy) < best_move)
        if best_score is None or score < best_score or tie:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]