def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Pick target resource: prefer those we are closer to than opponent.
    best_t = None
    best_key = None
    for r in resources:
        tx, ty = r[0], r[1]
        if (tx, ty) in obstacles:
            continue
        sd = dist((sx, sy), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        key = (od - sd, -sd, -tx, -ty)  # deterministic tie-breakers
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    # If no resources, head toward opponent a bit while avoiding obstacles.
    if best_t is None:
        best_t = (ox, oy)

    tx, ty = best_t
    # Evaluate next step toward target, with mild anti-opponent pressure and obstacle avoidance.
    def obstacle_pen(nx, ny):
        # small penalty for stepping adjacent to obstacles
        adj = 0
        for (bx, by) in obstacles:
            if abs(bx-nx) <= 1 and abs(by-ny) <= 1:
                adj += 1
        return adj

    best_delta = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = abs(nx - tx) + abs(ny - ty)
        od = abs(ox - tx) + abs(oy - ty)
        # Prefer reducing our distance; also slightly discourage letting opponent gain.
        val = -nd + (od - nd) * 0.01 - obstacle_pen(nx, ny) * 0.05
        key = (val, -nd, dx, dy)  # deterministic
        if best_val is None or key > best_val:
            best_val = key
            best_delta = (dx, dy)

    return [best_delta[0], best_delta[1]]