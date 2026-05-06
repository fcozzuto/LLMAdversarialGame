def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        dx = 0 if ox == x else (1 if ox > x else -1)
        dy = 0 if oy == y else (1 if oy > y else -1)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            nx, ny = x, y
        dme_best = 10**9
        race_best = -10**18

        for tx, ty in resources:
            d_me = dist(nx, ny, tx, ty)
            d_opp = dist(ox, oy, tx, ty)
            race = d_opp - d_me  # positive means we are closer than opponent
            if race > race_best or (race == race_best and d_me < dme_best):
                race_best = race
                dme_best = d_me

        # Additional pull to center-ish of resource set to reduce ties; deterministic.
        cx = sum(r[0] for r in resources) / len(resources)
        cy = sum(r[1] for r in resources) / len(resources)
        center_pull = -dist(nx, ny, cx, cy) * 0.001

        key = (race_best, center_pull, -dme_best, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [sign(ox - x), sign(oy - y)]