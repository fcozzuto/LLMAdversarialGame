def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target selection:
    # 1) Prefer resources we are at least as close to as the opponent (sd <= od)
    # 2) Among them, take the closest (sd)
    # 3) If none, take the resource opponent is closest to (od), as a fallback for contest.
    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if sd <= od:
            key = (0, sd, od, rx, ry)
        else:
            key = (1, od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Move selection:
    # 1) Move that best improves our lead (sd2-od2) (more negative is better)
    # 2) Then minimize our distance to target
    # 3) Then avoid clumping into opponent when not needed (distance to opponent)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        lead = sd2 - od2
        oppdist = man(nx, ny, ox, oy)
        score = (lead, sd2, -oppdist, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]