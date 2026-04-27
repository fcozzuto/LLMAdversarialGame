def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obs_set = {(p[0], p[1]) for p in obstacles}
    res_list = [(p[0], p[1]) for p in resources]

    def clamp_xy(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx + dy  # deterministic, cheap

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves.sort()

    # Pick a resource: favor those we can reach earlier than opponent.
    target = None
    best_race = None
    if res_list:
        for r in res_list:
            ds = dist((sx, sy), r)
            do = dist((ox, oy), r)
            race = do - ds  # positive means we are closer
            if best_race is None or race > best_race or (race == best_race and ds < dist((sx, sy), target)):
                best_race = race
                target = r
        if target is None:
            target = min(res_list, key=lambda r: dist((sx, sy), r))
    else:
        target = (sx, sy)

    # If no favorable race, switch to nearest resource to keep progressing.
    if res_list and best_race is not None and best_race <= 0:
        target = min(res_list, key=lambda r: dist((sx, sy), r))

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = clamp_xy(sx + dx, sy + dy)
        invalid = (nx, ny) in obs_set
        # Chebyshev keeps diagonal movement meaningful
        def cheb(p, q):
            return max(abs(p[0] - q[0]), abs(p[1] - q[1]))

        my_d = cheb((nx, ny), target)
        op_d = cheb((ox, oy), target)
        # Prefer: approach target, keep distance from opponent slightly, avoid obstacles.
        score = (-(my_d * 4 + invalid * 10) + (op_d - my_d) * 2)
        # Small bias to reduce distance overall to avoid oscillations.
        score += -dist((nx, ny), target) * 0.1
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]