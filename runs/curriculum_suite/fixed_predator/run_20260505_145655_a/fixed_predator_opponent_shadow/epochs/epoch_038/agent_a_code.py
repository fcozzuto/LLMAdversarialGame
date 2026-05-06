def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Prefer resources where we are (after moving) closer than opponent; if both chase, take nearer/faster.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = x, y
            dx, dy = 0, 0

        # Find best resource for this next position (small list, deterministic scan).
        cur_best = -10**18
        for tx, ty in resources:
            d_me = man(nx, ny, tx, ty)
            d_opp = man(ox, oy, tx, ty)
            # lead: positive means we are closer (good). Also reward faster acquisition and slight safety vs opponent.
            lead = d_opp - d_me
            val = lead * 1200 - d_me * 10 + (d_opp * 0.2)
            # If very close to opponent, discourage accidental moves that let them grab first.
            val -= max(0, 3 - (man(nx, ny, ox, oy))) * 15
            if val > cur_best:
                cur_best = val

        # Small tie-break: slightly reduce distance to opponent to contest, but not too much.
        tie = -man(nx, ny, ox, oy) * 0.01
        total = cur_best + tie
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]