def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None:
            obst.add((p[0], p[1]))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    best = [0, 0]
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Advantage: prefer resources where we are closer than opponent after this move.
        val = -0.1  # slight preference to move
        for rx, ry in resources:
            ds = max(abs(nx - rx), abs(ny - ry))
            do = max(abs(ox - rx), abs(oy - ry))
            # Primary: maximize (do - ds), secondary: minimize ds
            val += (do - ds) * 2.0 - ds * 0.03
        # Small tie-break: avoid standing still
        if dx == 0 and dy == 0:
            val -= 0.25
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best