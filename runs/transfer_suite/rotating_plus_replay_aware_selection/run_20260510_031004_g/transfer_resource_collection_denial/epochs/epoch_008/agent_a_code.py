def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    res = [(int(p[0]), int(p[1])) for p in resources]
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**9

    # Heuristic: move that minimizes our distance to good resource while maximizing our lead vs opponent.
    # Also lightly discourages approaching a resource too closely when opponent is already closer (denier).
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        our_best = 10**9
        lead_best = -10**9
        deny_best = 10**9

        for tx, ty in res:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            if sd < our_best:
                our_best = sd
            lead = od - sd  # positive means we are closer than opponent
            if lead > lead_best:
                lead_best = lead
            if od <= sd:  # opponent not farther; might be contested
                if od - sd < deny_best:
                    deny_best = od - sd

        # Priority: get lead (lead_best), then progress (our_best), then avoid giving opponent an edge (penalize negative deny).
        score = 2000 * lead_best - 50 * our_best - 200 * deny_best
        # Minor tie-break: prefer moves that reduce our distance to the top resource by raw sum distance.
        if lead_best < 0:
            score -= 10 * cheb(nx, ny, sx, sy)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]