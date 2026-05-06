def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        best = (0, 0)
        best_score = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacle_set:
                continue
            dopp = max(abs(nx - ox), abs(ny - oy))
            score = dpp = dpp = dopp
            if score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    best_t = None
    best_val = -10**9
    best_sd = 10**9
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd) * 100 - sd
        if val > best_val or (val == best_val and (sd < best_sd or (sd == best_sd and (rx, ry) < (best_t[0], best_t[1])))):
            best_val = val
            best_sd = sd
            best_t = (rx, ry)

    tx, ty = best_t
    best = (0, 0)
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"]):
            continue
        if (nx, ny) in obstacle_set:
            continue
        dist_t = cheb(nx, ny, tx, ty)
        dist_o = cheb(nx, ny, ox, oy)
        score = -dist_t * 1000 + dist_o
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]