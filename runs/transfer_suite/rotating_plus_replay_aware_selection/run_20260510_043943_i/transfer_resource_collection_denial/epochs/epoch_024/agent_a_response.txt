def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If can't move (all blocked around), stay.
    # Choose target: best resource by advantage = opp_dist - self_dist (want positive, but also closest).
    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Tie-break: prefer smaller sd and larger advantage.
            key = (-(od - sd), sd, rx, ry)  # smallest od-sd negative => largest advantage first
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
        # Evaluate each move by resulting position.
        best_move = [0, 0]
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            nsd = man(nx, ny, tx, ty)
            nod = man(nx, ny, ox, oy)  # how close we get to opponent (avoid getting denied too easily)
            # Compute whether opponent could steal in one step from their next positions.
            # Approximate by minimal distance from opponent after one move to our target.
            opp_min = 10**9
            for edx, edy in deltas:
                ex, ey = ox + edx, oy + edy
                if blocked(ex, ey):
                    continue
                d = man(ex, ey, tx, ty)
                if d < opp_min:
                    opp_min = d
            # If we are closer to target than opponent can become, prioritize collecting.
            # Also, discourage moves that increase nsd while opponent can get very close.
            score = (opp_min - nsd, -nsd, -nod, -abs(nx - tx) - abs(ny - ty), dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return [int(best_move[0]), int(best_move[1])]

    # No resources: evade and maximize distance from opponent and keep safe from obstacles.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)
        # Prefer moves that increase distance; tie-break toward center-ish.
        center_bias = -abs((nx - (w - 1) / 2)) - abs((ny - (h - 1) / 2))
        score = (d_opp, center_bias, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]