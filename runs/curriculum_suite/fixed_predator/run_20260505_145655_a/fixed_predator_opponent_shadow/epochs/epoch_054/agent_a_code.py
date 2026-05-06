def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best_t = resources[0]
    best_score = None
    for tx, ty in resources:
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Prefer resources where we are relatively closer; penalize long travel.
        score = (d_opp - d_me) * 1000 - d_me
        if best_score is None or score > best_score or (score == best_score and (tx, ty) < tuple(best_t)):
            best_score = score
            best_t = [tx, ty]

    tx, ty = best_t[0], best_t[1]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def move_score(nx, ny):
        d_me = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Micro-goal: reduce our distance to target, while increasing relative advantage.
        lead = (d_opp - d_me)
        # Obstacle pressure: avoid stepping next to obstacles (discourages tight traps).
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if in_bounds(xx, yy) and cell_blocked(xx, yy):
                    near_obs += 1
        return lead * 1000 - d_me - 2 * near_obs

    best_move = [0, 0]
    best_move_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if cell_blocked(nx, ny):
            continue
        sc = move_score(nx, ny)
        if best_move_score is None or sc > best_move_score or (sc == best_move_score and (dx, dy) < tuple(best_move)):
            best_move_score = sc
            best_move = [dx, dy]

    if best_move_score is None:
        return [0, 0]

    return best_move