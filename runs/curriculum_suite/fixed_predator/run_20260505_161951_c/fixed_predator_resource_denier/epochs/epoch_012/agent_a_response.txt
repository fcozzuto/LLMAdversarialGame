def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacle_set = set((a, b) for a, b in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    if not resources:
        best = (0, 0)
        best_score = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacle_set:
                continue
            # maximize separation from opponent to reduce interference
            s = cheb(nx, ny, ox, oy)
            if s > best_score or (s == best_score and (dx, dy) < best):
                best_score = s
                best = (dx, dy)
        return [best[0], best[1]]

    # pick target that we are relatively closer to (deny), otherwise still progress to a high-value resource
    best_t = None
    best_val = -10**18
    best_sd = 10**9
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd) * 100 - sd  # bigger means more denial / closer capture
        if val > best_val or (val == best_val and (sd < best_sd or (sd == best_sd and (rx, ry) < best_t))):
            best_val = val
            best_sd = sd
            best_t = (rx, ry)

    tx, ty = best_t

    # evaluate immediate moves by resulting best "deny" against remaining resource set
    best = (0, 0)
    best_move_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacle_set:
            continue
        # local lookahead: choose best resource from our next position
        mv_best_val = -10**18
        mv_best_sd = 10**9
        for rx, ry in resources:
            sd2 = cheb(nx, ny, rx, ry)
            od2 = cheb(ox, oy, rx, ry)
            val2 = (od2 - sd2) * 100 - sd2
            if val2 > mv_best_val or (val2 == mv_best_val and (sd2 < mv_best_sd)):
                mv_best_val = val2
                mv_best_sd = sd2
        # slight preference for moving toward target to break ties deterministically
        toward = cheb(nx, ny, tx, ty)
        score = mv_best_val * 1000 - toward
        if score > best_move_score or (score == best_move_score and (dx, dy) < best):
            best_move_score = score
            best = (dx, dy)

    return [best[0], best[1]]