def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx if False else (dx if dx > 0 else -dx) if dy == 0 else max(abs(dx), abs(dy))

    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    def score_cell(x, y, tx, ty):
        myd = dist(x, y, tx, ty)
        opd = dist(x, y, ox, oy)
        opp_to_target = dist(ox, oy, tx, ty)
        # Prefer getting closer to target; if opponent is also targeting it, keep some separation.
        base = -myd
        sep = opd
        # Reward distance from opponent when they can reach target very fast.
        if opp_to_target <= myd:
            base += 0.2 * sep
        return base

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Choose target resource with my advantage.
    best_target = None
    best_adv = -10**9
    best_dist = 10**9
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        adv = (opd - myd)
        # Strongly prefer resources I can reach strictly earlier.
        if myd < opd:
            if adv > best_adv:
                best_adv = adv
                best_target = (rx, ry)
        else:
            # If no clear advantage exists, track closest.
            if myd < best_dist and best_target is None:
                best_dist = myd
                best_target = (rx, ry)

    if best_target is None:
        # Fallback: move away/towards center deterministically.
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_target

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        v = score_cell(nx, ny, tx, ty)
        # Also slightly prefer staying within bounds and not moving onto opponent if adjacent.
        if dist(nx, ny, ox, oy) <= 0:
            v -= 5
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]