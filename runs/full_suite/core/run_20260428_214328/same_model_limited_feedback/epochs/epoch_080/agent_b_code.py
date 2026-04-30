def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def best_target():
        if not resources:
            return (w//2, h//2)
        best = None
        best_key = None
        for r in resources:
            myd = dist((sx, sy), r)
            opd = dist((ox, oy), r)
            adv = opd - myd
            key = (0, -adv, myd) if adv >= 0 else (1, myd, -adv)
            if best_key is None or key < best_key:
                best_key = key
                best = r
        return best

    target = best_target()
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    best_dxdy = None
    best_score = None
    for dx, dy, nx, ny in candidates:
        myd = dist((nx, ny), target)
        cur_myd = dist((sx, sy), target)
        opd = dist((ox, oy), target)
        # Prefer reducing distance to target; also prefer targets where we are closer than opponent.
        score = (myd, -((opd - myd) >= (opd - cur_myd)), abs(ny - oy) + abs(nx - ox))
        # Ensure deterministic tie-breaking: fixed ordering via (dx,dy)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_dxdy):
            best_score = score
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]