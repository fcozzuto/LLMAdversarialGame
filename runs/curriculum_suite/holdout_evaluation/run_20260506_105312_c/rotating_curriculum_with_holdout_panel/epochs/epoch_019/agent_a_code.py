def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Choose best next step by maximizing (opponent_reach_time - my_reach_time) with mild tiebreaks.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        myd0 = cheb(nx, ny, ox, oy)
        move_val = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Only consider resources we can plausibly claim (or at least not be hopelessly behind).
            diff = opd - myd
            if diff < -2:
                continue

            # Main: win-advantage; Secondary: absolute closeness; Tertiary: avoid stepping adjacent to opponent.
            val = diff * 18 - myd * 2
            if ry == oy:
                val -= 4  # discourage entering opponent row directly
            val -= (myd0 == 0) * 200  # hard penalty if collide positionally
            if opd == myd:
                val -= 2  # slightly prefer clear leads
            if val > move_val:
                move_val = val

        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]