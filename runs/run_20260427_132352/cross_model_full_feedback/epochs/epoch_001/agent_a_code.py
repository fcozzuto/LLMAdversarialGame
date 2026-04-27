def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((a[0], a[1]) for a in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def step_allowed(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def resource_priority(rx, ry):
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources closer to us, and generally closer overall
        return (do - ds, -ds, - (rx + 100*ry))  # tie-break deterministic

    target = None
    if resources:
        target = resources[0]
        bestp = resource_priority(target[0], target[1])
        for r in resources[1:]:
            p = resource_priority(r[0], r[1])
            if p > bestp:
                bestp = p
                target = r

    # If no resources, drift toward opponent side deterministically
    if not target:
        tx, ty = (w-1 if ox > sx else 0, h-1 if oy > sy else 0)
    else:
        tx, ty = target[0], target[1]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not step_allowed(nx, ny):
            continue
        # Move quality: reduce distance to target; small bias to avoid staying
        d = dist((nx, ny), (tx, ty))
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        # Also consider immediate blocking by choosing cells that reduce opponent advantage when feasible
        opp_d = dist((ox, oy), (tx, ty))
        my_adv = opp_d - (d)
        score = my_adv*1000 - d*10 - stay_pen
        # Deterministic tie-break: prefer lexicographically smaller dx, then dy
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # Fallback if all moves blocked (should be rare)
    dx, dy = best_move
    if not step_allowed(sx + dx, sy + dy):
        return [0, 0]
    return [dx, dy]