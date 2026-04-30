def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources") or []
    res = [(int(p[0]), int(p[1])) for p in resources]
    if (sx, sy) in obs:
        return [0, 0]
    if (sx, sy) in res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))

    if not res:
        best = (0, 0, -10**9)
        for dx, dy, nx, ny in valid:
            dopp = cheb(nx, ny, ox, oy)
            score = -dopp
            if score > best[2] or (score == best[2] and (dx, dy) < (best[0], best[1])):
                best = (dx, dy, score)
        return [best[0], best[1]]

    # Pick a target resource where we are relatively closer than the opponent.
    best_r = None
    best_val = -10**18
    best_ds = 10**9
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = do - ds  # positive => we are closer
        if val > best_val or (val == best_val and ds < best_ds) or (val == best_val and ds == best_ds and (rx, ry) < best_r):
            best_val = val
            best_ds = ds
            best_r = (rx, ry)

    rx, ry = best_r
    best_move = (0, 0, -10**18)
    for dx, dy, nx, ny in valid:
        ds_next = cheb(nx, ny, rx, ry)
        do_here = cheb(ox, oy, rx, ry)
        # Assume opponent roughly holds; advantage favors getting closer faster.
        adv = (do_here - ds_next)
        opp_escape = cheb(nx, ny, ox, oy)
        score = 6 * adv - ds_next - 0.05 * opp_escape
        if score > best_move[2] or (score == best_move[2] and (dx, dy) < (best_move[0], best_move[1])):
            best_move = (dx, dy, score)

    return [best_move[0], best_move[1]]