def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if resources is None:
        resources = []
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (dist(nx, ny, tx, ty), dist(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_key = None
    best_move = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        opp_step = dist(nx, ny, ox, oy)
        # Interception/contestion: favor moves where you are strictly closer to some resource than opponent.
        best = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            diff = od - sd  # positive means you can likely reach first
            # Small tie-break to prefer nearer capture and to slightly reduce proximity to opponent.
            key = (-diff, sd, opp_step)
            if best is None or key < best:
                best = key
        if best_key is None or best < best_key:
            best_key = best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]