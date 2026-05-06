def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best_move = [0, 0]
        best_score = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacle_set:
                nx, ny = x, y
            dopp = cheb(nx, ny, ox, oy)
            score = dopp
            if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
                best_score = score
                best_move = [dx, dy]
        return best_move

    # Pick a principal target: maximize opponent advantage at that resource.
    best_t = None
    best_val = -10**18
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd) * 100 - sd
        if best_t is None or val > best_val or (val == best_val and (sd < cheb(x, y, best_t[0], best_t[1]))):
            best_val = val
            best_t = (rx, ry)

    rx, ry = best_t
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacle_set:
            nx, ny = x, y
        sd = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Primary: increase opponent-self gap; Secondary: reduce self distance; Tertiary: nudge to improve chance on other resources.
        gap = (od - sd) * 100 - sd
        sec = 0
        for (ar, ab) in resources:
            if (ar, ab) == (rx, ry):
                continue
            dself = cheb(nx, ny, ar, ab)
            dop = cheb(ox, oy, ar, ab)
            if dop - dself >= 1:
                sec = dself
                break
        score = gap * 1000 - sec
        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]
    return best_move