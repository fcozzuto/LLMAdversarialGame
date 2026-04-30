def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obs_pen(x, y):
        p = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))

    best = None
    if resources:
        # Aggressive resource contest: prefer moves where we get closer than the opponent.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            op = obs_pen(nx, ny)
            # Choose the resource we would approach best from (nx, ny)
            best_r_self = None
            best_r_score = None
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # Lower is better for us: distance plus opponent contest pressure
                # (If opponent is farther, we get a bonus; if closer, we get penalized.)
                score = sd + 0.4 * od - 0.7 * (od - sd)
                if best_r_score is None or score < best_r_score:
                    best_r_score = score
                    best_r_self = (sd, od)
            sd, od = best_r_self
            # Additional immediate incentive to reduce our distance to the chosen resource
            # and discourage clustering near obstacles.
            total = 3.0 * sd + 1.0 * (od - sd) + 0.8 * op
            if best is None or total < best[0]:
                best = (total, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # No resources visible: reposition toward the corner farthest from opponent, avoiding obstacles.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    target = None
    best_corner_key = None
    for cx, cy in corners:
        k = man(cx, cy, ox, oy)
        if best_corner_key is None or k > best_corner_key:
            best_corner_key = k
            target = (cx, cy)

    tx, ty = target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        op = obs_pen(nx, ny)
        total = man(nx, ny, tx, ty) + 2.0 * op + 0.3 * man(nx, ny, ox, oy)
        if best is None or total < best[0]:
            best = (total, dx, dy)

    return [best[1], best[2]] if best else [0, 0]