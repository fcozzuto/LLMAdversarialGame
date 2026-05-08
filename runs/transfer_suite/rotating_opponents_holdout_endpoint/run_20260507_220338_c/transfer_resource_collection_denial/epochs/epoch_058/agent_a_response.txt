def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Select target with a stronger time-to-claim heuristic vs opponent.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # If we can arrive no later, prioritize shortest our arrival.
        # Otherwise, contest the resource where opponent's lead is smallest
        # and their arrival is not extremely early.
        if sd <= od:
            key = (0, sd, od)
        else:
            lead = od - sd
            key = (1, lead, od)
        if best is None or key < best[0]:
            best = (key, (rx, ry, sd, od))
    if best is None:
        return [0, 0]
    tx, ty, sd, od = best[1]

    # If already on resource, collect.
    if sx == tx and sy == ty:
        return [0, 0]

    # Choose move minimizing our time-to-target, with extra penalty if opponent is racing.
    best_move = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            sd_next = man(nx, ny, tx, ty)
            # If opponent is closer/equal to the target, heavily discourage moves that keep us behind.
            # Otherwise, just reduce our distance.
            behind = od - sd_next
            penalty = 0
            if behind >= 0:
                penalty = 10 * (behind + 1)
            # Small tie-breaker to avoid oscillations: prefer moves that reduce opponent distance too.
            od_next = man(nx, ny, tx, ty)  # proxy using our pos; deterministic small bias
            key = (sd_next + penalty, penalty, -od_next, abs(nx - tx) + abs(ny - ty))
            if best_move is None or key < best_move[0]:
                best_move = (key, [dx, dy])

    return best_move[1]