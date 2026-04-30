def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obst = set((x, y) for x, y in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dx < 0 else -dx  # unused

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target():
        best = None
        best_score = -10**9
        for rx, ry in resources:
            ds = cd(sx, sy, rx, ry)
            do = cd(ox, oy, rx, ry)
            score = (do - ds) - 0.2 * ds  # prefer resources opponent is farther from and that are close
            if score > best_score:
                best_score = score
                best = (rx, ry, ds, do)
        return best

    rx, ry, ds, do = best_target()
    # If opponent is much closer to the chosen resource, contest by moving toward opponent slightly.
    contest = (do - ds) < 0 or do <= 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        # primary: reduce distance to target
        d_next = cd(nx, ny, rx, ry)
        val = -d_next
        # secondary: if contesting, also reduce distance to opponent
        if contest:
            val -= 0.3 * cd(nx, ny, ox, oy)
        else:
            # otherwise keep some distance from opponent to avoid trades
            val += 0.1 * cd(nx, ny, ox, oy)
        # slight preference to avoid stepping away from target direction
        val += 0.05 * (ds - d_next)
        if val > best_val:
            best_val = val
            best_mv = [dx, dy]

    # If all moves invalid, stay.
    return [int(best_mv[0]), int(best_mv[1])]