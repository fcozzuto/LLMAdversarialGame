def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target: deterministic "I can get it first, else pick closest threat"
    best_key = None
    tx, ty = resources[0]
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer resources I'm not farther from than opponent, then smaller myd, then farther from opponent.
        key = (0 if myd <= opd else 1, myd, -opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            tx, ty = rx, ry

    # Scoring moves: reduce my distance to target; if tie, keep/avoid giving opponent an easy grab
    best_mv = [0, 0]
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = man(nx, ny, tx, ty)
        myd1 = man(sx, sy, tx, ty)
        oppd = man(ox, oy, tx, ty)

        # Bonus if we are (or become) strictly closer than opponent to the target.
        win_bonus = 0
        if myd2 <= oppd:
            win_bonus = 100 - myd2

        # Discourage moving into proximity where opponent can immediately collect a resource.
        # Find the best (closest) resource for opponent after our move: approximate by current opponent distances.
        mind_op = 10**9
        for rx, ry in resources:
            od = man(ox, oy, rx, ry)
            if od < mind_op:
                mind_op = od

        # Discourage stepping away from target; small preference for moving (not required).
        step_pen = 0 if (dx == 0 and dy == 0) else -0.5

        sc = (win_bonus + (myd1 - myd2) * 10 - myd2) + step_pen + (-0.1 * mind_op)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = [dx, dy]

    # Fallback if all moves invalid
    return best_mv