def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_obs(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    # Pick best deterministic target among resources
    best_t = None
    best_key = None
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        myd = dist(sx, sy, tx, ty)
        opd = dist(ox, oy, tx, ty)
        contest = 1 if myd <= opd else 0
        center = -(abs(tx - cx) + abs(ty - cy))
        key = (
            contest * 100 + (opd - myd) * 3 + (-myd) * 1.5 + center * 0.1 - adj_obs(tx, ty) * 0.2,
            -opd, -myd, tx, ty
        )
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = dist(sx, sy, tx, ty)

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = dist(nx, ny, tx, ty)
        my_improve = curd - nd
        oppd = dist(ox, oy, tx, ty)
        # Prefer approaching target; also slight preference if opponent is relatively farther.
        val = (my_improve * 10 + (-nd) * 2 + (oppd - nd) * 0.3 + (-adj_obs(nx, ny)) * 0.25)
        key = (val, -nd, dx, dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]