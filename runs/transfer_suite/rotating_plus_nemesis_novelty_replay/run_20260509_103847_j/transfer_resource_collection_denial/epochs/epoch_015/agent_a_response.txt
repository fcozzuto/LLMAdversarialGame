def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target we are closest to, but avoid letting opponent also get too good access.
    def target_choice():
        best = None
        best_key = None
        for r in resources:
            sd = man((sx, sy), r)
            od = man((ox, oy), r)
            # Key: maximize advantage (sd-od), then minimize our distance, then coords
            key = (-(od - sd), sd, r[0], r[1])
            if best_key is None or key < best_key:
                best_key, best = key, r
        return best

    target = target_choice()
    # If opponent is already substantially closer to the chosen target, pick next best.
    sd0 = man((sx, sy), target)
    od0 = man((ox, oy), target)
    if od0 + 2 < sd0 and len(resources) > 1:
        alt_best = None; alt_key = None
        for r in resources:
            sd = man((sx, sy), r)
            od = man((ox, oy), r)
            key = (-(od - sd), sd, r[0], r[1])
            if alt_best is None or key < alt_key:
                alt_best, alt_key = r, key
        target = alt_best

    # Move to reduce our distance to target; add a small preference to increase opponent distance.
    best_move = (0, 0); best_key = None
    tx, ty = target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = abs(nx - tx) + abs(ny - ty)
        d_opp = abs((nx + (ox - sx)) - tx) + abs((ny + (oy - sy)) - ty)  # deterministic proxy
        # Key: minimize self distance, then maximize proxy opponent distance, then dx/dy order
        key = (d_self, -(d_opp), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]