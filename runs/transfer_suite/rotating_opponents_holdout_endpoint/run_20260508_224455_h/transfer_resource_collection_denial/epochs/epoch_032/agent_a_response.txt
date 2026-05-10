def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        dm = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can beat opponent on (do-dm large), then closer overall, then deterministic.
        key = (-(do - dm), dm, do, rx * 131 + ry * 17)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        rx, ry = resources[0][0], resources[0][1]
        tx, ty = rx, ry
    else:
        tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    chosen = (0, 0)
    chosen_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dm2 = man(nx, ny, tx, ty)
        # Deny: also try to move away from positions that reduce opponent access to the same target.
        do2 = man(ox, oy, tx, ty)
        # If opponent is strictly closer to the target, prioritize making progress while also increasing their distance from our current neighborhood.
        # Deterministic small preference: prefer moves that reduce our distance to target most.
        score_key = (dm2, -do2, dx * 3 + dy)
        if chosen_key is None or score_key < chosen_key:
            chosen_key = score_key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]