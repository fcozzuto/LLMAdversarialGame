def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    # Pick the resource where we have the biggest (opponent - us) advantage right now.
    best_t = None
    best_adv = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd
        if best_adv is None or adv > best_adv:
            best_adv = adv
            best_t = (rx, ry)

    tx, ty = best_t

    # Move one step to reduce our distance to target; break ties by improving advantage next step.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        myd = md(nx, ny, tx, ty)
        od = md(ox, oy, tx, ty)
        adv_next = od - myd
        # primary: smaller our distance to target; secondary: larger advantage
        key = (myd, -adv_next, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]