def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_adv_from(x, y):
        best = None
        best_myd = None
        for rx, ry in resources:
            myd = cheb(x, y, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means I'm closer
            if best is None or adv > best or (adv == best and myd < best_myd):
                best = adv
                best_myd = myd
        return best, best_myd

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break order already in list; pick first best.
    best_move = (0, 0)
    best_score = None
    best_approach = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        adv, myd = best_adv_from(nx, ny)
        # Prefer higher advantage; then closer to that best resource; then also avoid giving opponent advantage.
        opd_best, _ = best_adv_from(ox, oy)  # from opponent current cell (constant)
        # opd_best is opd - opd = 0 always, but keep deterministic structure without relying on it.
        score = (adv, -myd, -cheb(nx, ny, ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
            best_approach = myd

    # If for some reason all moves blocked, stay.
    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]