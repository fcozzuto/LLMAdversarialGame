def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a contested target: minimize (our_dist - opp_dist), then our_dist, then coords
    best_r = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) and (rx, ry) not in blocked:
            continue
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        key = (d1 - d2, d1, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # If we are significantly behind, prioritize denying (move to increase opp distance to target)
    our_to = cheb(sx, sy, tx, ty)
    opp_to = cheb(ox, oy, tx, ty)
    deny_mode = (our_to > opp_to)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(nx, ny, ox, oy)  # closeness to opponent for potential harassment
        opp_to_after = cheb(ox, oy, tx, ty)
        # small deterministic tie-breaker using coordinates
        key_x = nx * 100 + ny

        if deny_mode:
            # Maximize: increase opponent-to-target distance proxy via our position (moving toward target often reduces it for opp too)
            # Instead, we try to move away from their likely route by moving toward our current target but with extra penalty if it makes us "too near" opponent.
            val = (oppd * 0.3) - myd + (0.05 * (sx - nx)) - key_x * 1e-6
        else:
            # Standard: go to our contested target and avoid getting too close to opponent if it helps them
            val = (-myd * 1.0) + (cheb(ox, oy, tx, ty) * 0.05) + (oppd * 0.02) - key_x * 1e-6

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    # As a last resort, if no move was valid, stay
    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]