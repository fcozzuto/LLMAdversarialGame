def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles if p is not None)
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose resource: prefer smaller distance for self, and farther from opponent.
    best = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Value: lower is better. Reward us being closer.
        val = (ds * 10) - (do * 7)
        # Tie-break with nearer center-ish to reduce wandering.
        val += cheb(rx, ry, (w - 1) // 2, (h - 1) // 2)
        if best_val is None or val < best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference: minimize distance to target; avoid obstacles; slight anti-jitter by preferring direction.
    bestm = (0, 0)
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        dnew = cheb(nx, ny, tx, ty)
        dcur = cheb(sx, sy, tx, ty)
        # Prefer moves that reduce distance; then exact tie by direction alignment to avoid lateral drift.
        improve = 0 if dnew >= dcur else 1
        align = 0
        if tx > sx: align += 1 if dx > 0 else 0
        if tx < sx: align += 1 if dx < 0 else 0
        if ty > sy: align += 1 if dy > 0 else 0
        if ty < sy: align += 1 if dy < 0 else 0
        score = (0 if improve else 1, dnew, -align, dx, dy)
        if bestscore is None or score < bestscore:
            bestscore = score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]