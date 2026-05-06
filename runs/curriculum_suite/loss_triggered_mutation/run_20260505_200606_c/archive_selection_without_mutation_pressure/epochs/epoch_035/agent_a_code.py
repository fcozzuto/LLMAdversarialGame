def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a promising target resource based on advantage vs opponent (deterministic)
    best_target = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        adv = dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry)
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)
        elif adv == best_adv:
            # tie-break by nearer to us, then lexicographic
            da = dist(sx, sy, rx, ry)
            db = dist(sx, sy, best_target[0], best_target[1])
            if da < db or (da == db and (rx, ry) < best_target):
                best_target = (rx, ry)

    tx, ty = best_target

    # Score candidate move by resulting advantage; add mild preference to progress toward target
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        our_d = dist(nx, ny, tx, ty)
        target_adv = dist(ox, oy, tx, ty) - our_d

        # Consider also competition over nearest resource after move
        best_comp = -10**18
        for rx, ry in resources:
            our_dr = dist(nx, ny, rx, ry)
            opp_dr = dist(ox, oy, rx, ry)
            comp = opp_dr - our_dr
            if comp > best_comp:
                best_comp = comp

        # Combine: prioritize competitive advantage; then progress to target; then center-ish tie-break
        score = 10 * best_comp + 2 * target_adv - our_d
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prefer staying aligned with target, then lower lexicographic move
            if (dist(nx, ny, tx, ty) < dist(sx + best_move[0], sy + best_move[1], tx, ty)) or \
               (dist(nx, ny, tx, ty) == dist(sx + best_move[0], sy + best_move[1], tx, ty) and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]