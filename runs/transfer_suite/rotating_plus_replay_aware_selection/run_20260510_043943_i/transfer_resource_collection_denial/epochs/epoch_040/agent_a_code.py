def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def drift_target():
        cx = (w - 1) // 2
        cy = (h - 1) // 2
        return cx, cy

    tx, ty = drift_target()

    if not resources:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                nx, ny = sx, sy
            score = -man(nx, ny, tx, ty)
            key = (score, -abs(nx - tx) - abs(ny - ty), -dx, -dy)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1]

    best_key = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
        # Prefer moves that let us be the first to reach a resource; avoid giving the opponent wins.
        score = 0
        min_self = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds < min_self:
                min_self = ds
            if do < min_opp:
                min_opp = do
            # Big bonus if we are closer (race), penalty if opponent closer.
            lead = do - ds
            val = lead * 120 - ds * 2
            if ds == 0:
                val += 10**8
            if do == 0 and ds != 0:
                val -= 10**7
            score += val
        # Secondary: reduce distance to nearest resource; also reduce opponent's nearest distance.
        score += -min_self * 5 + min_opp * 0.5
        # Deterministic tie-break: lexicographic preference by move order and score.
        key = (score, -min_self, -abs(ox - nx) - abs(oy - ny), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move