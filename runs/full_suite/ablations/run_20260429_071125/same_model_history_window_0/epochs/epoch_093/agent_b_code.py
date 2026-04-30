def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b):  # Chebyshev for diagonal steps
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # Pick target resource where we have maximal "lead" over opponent
    best = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles: 
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = (do - ds, -ds, rx, ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    if best is None:
        # No resources: move to reduce distance to opponent's corner heuristically
        tx, ty = (w-1 if sx < w//2 else 0, h-1 if sy < h//2 else 0)
        target = (tx, ty)
    else:
        target = best[1]

    tx, ty = target
    # If target unreachable due to being surrounded, fall back to any reachable resource
    if target in obstacles:
        target = None
        for r in resources:
            if tuple(r) not in obstacles:
                target = tuple(r); break
        if target is None:
            target = (sx, sy)
        tx, ty = target

    def cell_ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    # Score candidate moves by progress to target; add mild avoidance of opponent
    best_move = (0, 0); best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        dself = dist((nx, ny), (tx, ty))
        # Prefer also not giving opponent a too-easy steal: estimate if opponent gets closer to target
        dopp = dist((ox, oy), (tx, ty))
        # Encourage approaching opponent only when it helps reach the target sooner (small)
        dopp_move = dist((ox, oy), (tx, ty)) - 0  # static; keep deterministic
        val = -dself * 100 + (dopp - dself) * 10 - (abs(nx-ox)+abs(ny-oy)) * 0.5
        # If currently on target, just stay (collect) or move minimally to avoid obstacles
        if (sx, sy) == (tx, ty):
            val += 1e6
        # Small bias to keep moving if tie: closer to target
        if dself == 0:
            val += 10000
        if val > best_val:
            best_val = val; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]