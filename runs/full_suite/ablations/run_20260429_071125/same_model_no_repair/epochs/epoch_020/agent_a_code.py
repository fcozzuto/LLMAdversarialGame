def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def risk(x, y):
        if (x, y) in occ:
            return 10**9
        r = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (x + dx, y + dy) in occ:
                r += 9
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in occ:
                r += 4
        return r

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    # If very few resources remain, bias toward closest safe resource.
    bias_close_only = observation.get("remaining_resource_count", len(resources)) <= 3

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        rr = risk(nx, ny)
        if rr > 10**8:
            continue

        # Choose the best resource from the NEXT position.
        best_resource_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            d_self = manh(nx, ny, rx, ry)
            d_opp = manh(ox, oy, rx, ry)

            if d_opp == 0 and d_self > 0:
                # Opponent on a resource: prioritize blocking by heading to its closest neighbors.
                # Still allow capturing if immediately adjacent.
                if d_self == 1:
                    val = 10**6 - d_self
                else:
                    val = -10**6 + (d_opp - d_self)
            else:
                # Positive when we are closer than opponent; scale to win contests.
                contest = (d_opp - d_self)
                # Prefer nearer for own capture; penalize letting opponent keep initiative.
                val = contest * 90 - d_self * (1.5 if not bias_close_only else 6.0)

                # Extra deterrence: avoid stepping onto likely dead-end funnel near obstacles.
                # (Approximated by additional neighbor risk around the resource direction.)
                if contest < 0 and rr > 0:
                    val -= rr * 3

                # If already at a resource, force it.
                if (nx, ny) == (rx, ry):
                    val = 10**9

            if val > best_resource_val:
                best_resource_val = val

        total = best_resource_val - rr
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]