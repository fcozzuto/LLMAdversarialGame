def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not res:
        return [0, 0]

    # Pick a resource where we are most likely to race first (minimize mydist-opdist)
    best = None
    for r in res:
        rx, ry = r[0], r[1]
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        key = (myd - opd, myd, -opd, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Move that most reduces our distance to the chosen target.
    # If tie, prefer increasing opponent distance to the target.
    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = man(nx, ny, tx, ty)
        opd2 = man(ox, oy, tx, ty)
        key = (myd2, -opd2, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]