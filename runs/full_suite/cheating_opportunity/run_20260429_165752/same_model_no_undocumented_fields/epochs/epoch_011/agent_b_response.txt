def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs.add((int(o[0]), int(o[1])))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    valids = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                valids.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if inb(x, y) and (x, y) in obs:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    if valids:
        # Pick resource where we have the biggest "win" over opponent (smallest our-opp distance).
        best_r = None
        best_gap = None
        for rx, ry in valids:
            our_d = cheb(x, y, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            gap = our_d - opp_d
            if best_r is None or gap < best_gap or (gap == best_gap and (rx + ry) < (best_r[0] + best_r[1])):
                best_r = (rx, ry)
                best_gap = gap
        tx, ty = best_r
    else:
        # No resources visible: go to center-ish.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Score each move by progress to target, avoid helping opponent, slight separation.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        d_to_t = cheb(nx, ny, tx, ty)
        d_opp_to_t = cheb(ox, oy, tx, ty)

        # Helps opponent if they are much closer to same target; we try to avoid that by increasing our distance if locked.
        # Also maintain separation from opponent.
        sep = cheb(nx, ny, ox, oy)

        # Lower is better.
        score = d_to_t + 0.25 * (d_opp_to_t - cheb(ox, oy, tx, ty)) - 0.05 * sep
        # Deterministic tie-break: prefer moving closer in x, then y, then diagonals.
        score = score * 1000 + (abs(nx - ox) + abs(ny - oy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move