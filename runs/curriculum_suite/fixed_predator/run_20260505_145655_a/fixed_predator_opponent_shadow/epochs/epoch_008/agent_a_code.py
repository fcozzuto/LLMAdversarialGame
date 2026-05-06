def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best = None
    best_key = None
    for rx, ry in resources:
        myd = man(x, y, rx, ry)
        opd = man(ox, oy, rx, ry)
        gap = opd - myd  # positive => we are closer (better for us)
        key = (gap, -myd)  # maximize gap; tie => smaller myd
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    myd = man(x, y, rx, ry)
    oppd = man(ox, oy, rx, ry)

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = man(nx, ny, rx, ry)
        # prefer moves that keep/extend our advantage on chosen target, also avoid moving toward opponent
        opp_to_us_before = man(ox, oy, x, y)
        opp_to_us_after = man(ox, oy, nx, ny)
        gap2 = oppd - myd2
        progress = myd - myd2
        key = (gap2, progress, opp_to_us_after, -myd2, dx == 0 and dy == 0)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]