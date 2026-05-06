def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    tx, ty = min(resources, key=lambda r: (manh(sx, sy, r[0], r[1]), r[0], r[1]))

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = manh(nx, ny, tx, ty)
        do = manh(ox, oy, tx, ty)
        adv = do - ds  # higher is better for us
        tie = (abs(dx) + abs(dy), (dx, dy))
        key = (-adv, ds, tie)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]
    return best_move