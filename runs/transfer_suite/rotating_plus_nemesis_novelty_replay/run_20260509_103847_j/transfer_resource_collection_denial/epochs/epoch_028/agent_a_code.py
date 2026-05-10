def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def pick_target():
        same_row = [r for r in resources if r[1] == oy]
        pool = same_row if same_row else resources
        best = None
        best_key = None
        for rx, ry in pool:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # If opponent is sweeping a row, contest that row first.
            # Otherwise, prioritize resources where we are closer (od - sd high),
            # with a strong preference to being closer than the opponent.
            if same_row:
                key = (0, sd, od, rx, ry)
            else:
                closer = 0 if sd <= od else 1
                key = (closer, -(od - sd), sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = pick_target()

    best_move = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue
        d = man(nx, ny, tx, ty)
        # Tie-break: reduce the opponent's advantage over this target
        # and prefer diagonal progress when tied.
        od_next = man(ox, oy, tx, ty)
        key = (d, od_next - d, abs(dx) + abs(dy), dx, dy)
        if best_d is None or key < best_d:
            best_d = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]