def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_from(px, py):
        best = None
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            lead = od - sd  # positive means we are closer or equal
            # Prefer we are no worse; among those, nearer.
            # If we're worse, pick smallest disadvantage (largest lead) then nearer for tie-break.
            if lead >= 0:
                key = (0, -lead, sd, rx, ry)
            else:
                key = (1, lead, sd, rx, ry)  # lead negative: closer to 0 is better
            if best is None or key < best:
                best = key
        # Return a comparable scalar-ish value derived from key
        if best[0] == 0:
            # we can reach at least as fast: score by (lead, -sd)
            lead = -best[1]
            sd = best[2]
            return (1, lead, -sd)
        else:
            # we are behind: score by (lead close to 0, -sd)
            lead = best[1]
            sd = best[2]
            return (0, lead, -sd)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    base = best_from(sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = best_from(nx, ny)
        # tie-break: keep improving target pressure; deterministic ordering by move tuple
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    # If movement doesn't change strategic value, make a deterministic bias toward decreasing our distance to nearest resource
    if best_val == base:
        best_dist = None
        biased = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dmin = None
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
            if best_dist is None or dmin < best_dist or (dmin == best_dist and (dx, dy) < biased):
                best_dist = dmin
                biased = (dx, dy)
        best_move = biased

    return [int(best_move[0]), int(best_move[1])]