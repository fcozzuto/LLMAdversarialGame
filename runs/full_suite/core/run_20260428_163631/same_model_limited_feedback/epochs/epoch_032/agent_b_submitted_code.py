def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    def clamp_step(x, y):
        if x < 0:
            return -1
        if x > 0:
            return 1
        return 0

    # Target selection: maximize (opponent reach advantage) - self distance
    tx, ty = sx, sy
    best = -10**18
    found = False
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # prefer resources that opponent is farther from; tie-break by closeness
        val = (od - sd) * 1000 - sd
        if val > best:
            best = val
            tx, ty = rx, ry
            found = True

    # If no resources, just move away from opponent if possible, else hold
    if not found:
        tx, ty = sx - clamp_step(ox - sx), sy - clamp_step(oy - sy)

    best_move = (0, 0)
    best_score = -10**18
    cur_sd = dist(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist(nx, ny, tx, ty)
        od = dist(nx, ny, ox, oy)
        # Approach target; if too close to opponent, heavily discourage
        score = (cur_sd - nd) * 10 - nd
        if od <= 1:
            score -= 50
        if (nx, ny) == (tx, ty):
            score += 10000
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]