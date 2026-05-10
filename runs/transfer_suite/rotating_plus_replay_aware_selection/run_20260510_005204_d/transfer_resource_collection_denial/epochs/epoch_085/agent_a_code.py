def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    inv = 0
    if turns_remaining <= 8:
        inv = 1  # late-game: be more greedy toward closest resource

    best_move = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; emulate deterministically

        myd_best = 10**9
        opd_best = 10**9
        val = 0

        # Prefer immediate collection
        if (nx, ny) in set(tuple(r) for r in resources):
            val += 10**6

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            myd_best = myd if myd < myd_best else myd_best
            opd_best = opd if opd < opd_best else opd_best
            # Main: increase relative winning chances (opponent farther than we are)
            rel = opd - myd
            # Secondary: prefer smaller myd (reach earlier), and avoid giving opponent a "now" grab
            immediate_threat = (cheb(ox, oy, rx, ry) == 0)
            val += rel * 10
            val += (-myd) * (20 if inv else 10)
            if immediate_threat:
                val -= 200

        # Add small penalty for staying when not optimal
        if dx == 0 and dy == 0:
            val -= 3
        # Deterministic tie-break: prefer moving toward lower coordinates if scores equal
        tie_key = (0, -nx, -ny)

        if best_move[0] is None or val > best_move[1] or (val == best_move[1] and tie_key > best_move[0]):
            best_move = (tie_key, val)
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]