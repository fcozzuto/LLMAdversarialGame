def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    res_set = set(tuple(p) for p in resources)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a primary target deterministically: strongest "go-get" relative to opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer: I can reach first; then smaller my distance; then farther from opponent (tie-break).
        key = (0 if myd <= opd else 1, myd, -opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Score after my move: capture immediate resource; otherwise improve advantage on a target.
        immediate = 1 if (nx, ny) in res_set else 0
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        adv = opd - myd  # positive if I become closer than opponent
        # Secondary tie-break: reduce distance to nearest resource if my main advantage is similar.
        nearest = None
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if nearest is None or d < nearest:
                nearest = d
        key = (0 if immediate else 1, -adv, myd, nearest if nearest is not None else 999, dx, dy)

        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]