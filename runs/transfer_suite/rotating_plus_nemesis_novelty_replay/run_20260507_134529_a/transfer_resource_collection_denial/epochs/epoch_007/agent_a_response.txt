def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (0 if ds <= do else 1, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    cur_ds = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Prefer: reach target ASAP, keep/extend advantage, and avoid approaching opponent too closely.
        # Tie-break by small "move cost" toward target to reduce oscillations.
        adv = 0 if ds2 <= do2 else 1
        opp_dist = cheb(nx, ny, ox, oy)
        score = (adv, ds2, -do2, -opp_dist, abs(nx - sx) + abs(ny - sy), rx := tx, ry := ty)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if (sx + dx, sy + dy) in obstacles:
        return [0, 0]
    return [dx, dy]