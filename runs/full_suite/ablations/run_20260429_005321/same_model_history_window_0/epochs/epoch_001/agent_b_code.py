def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = d2(sx, sy, rx, ry)
            do = d2(ox, oy, rx, ry)
            # Prefer resources we are closer to; break ties by nearer and then by position
            key = (ds - do, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # No resources visible: drift to center
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            dist = d2(nx, ny, tx, ty)
            # Also discourage moving into cells where opponent is much closer to the same target
            opp_dist_next = d2(ox, oy, tx, ty)
            # tie-break with moving "toward" by Manhattan-ish sign consistency
            toward = abs(nx - tx) + abs(ny - ty)
            score = (dist - 0.25 * opp_dist_next, toward, nx, ny, dx, dy)
        else:
            dist = d2(nx, ny, tx, ty)
            score = (dist, nx, ny, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]