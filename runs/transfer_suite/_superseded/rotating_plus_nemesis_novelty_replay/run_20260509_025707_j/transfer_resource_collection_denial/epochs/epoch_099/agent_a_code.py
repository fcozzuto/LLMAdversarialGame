def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prefer moves that keep our reach advantage over the best available resource.
    best_move = [0, 0]
    best_score = -10**18
    best_primary = 10**18
    best_secondary = 10**18

    # Deterministic bias: roughly move toward opponent's current row/col to intercept paths.
    bias_x = ox if 0 <= ox < w else sx
    bias_y = oy if 0 <= oy < h else sy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        primary = 10**18
        secondary = 10**18
        score = 0

        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # If we can beat opponent on this resource, it pays heavily; otherwise penalize.
            adv = od - sd
            # Encourage taking closer resources, but dominated by ensuring advantage vs denier.
            val = adv * 100 - sd

            # Track the best (closest-with-advantage) resource for tie-breaking.
            if sd < primary:
                primary = sd
                secondary = sd + 2 * man(ox, oy, rx, ry)

            score += val

        # Secondary shaped by alignment with bias to avoid getting stuck behind denier.
        score -= 0.2 * (abs(nx - bias_x) + abs(ny - bias_y))

        # Tie-breaking: maximize score, then minimize primary (distance to best resource), then minimize overall.
        if score > best_score or (score == best_score and (primary < best_primary or (primary == best_primary and secondary < best_secondary))):
            best_score = score
            best_primary = primary
            best_secondary = secondary
            best_move = [dx, dy]

    return best_move