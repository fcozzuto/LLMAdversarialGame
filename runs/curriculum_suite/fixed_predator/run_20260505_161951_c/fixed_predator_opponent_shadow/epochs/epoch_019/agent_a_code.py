def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # fall back: move to increase separation from opponent deterministically
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = (-(abs(nx - ox) + abs(ny - oy)), dx, dy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    res_set = set(resources)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        # choose best resource from this resulting position
        best_r = None
        for rx, ry in resources:
            selfd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)
            race = oppd - selfd  # positive => we're closer
            if (nx, ny) == (rx, ry):
                race += 10**6
            # prefer being closer (lower selfd) and more in-race; small tie-breaks deterministic
            key = (race, -selfd, -man(nx, ny, ox, oy), rx, ry)
            if best_r is None or key > best_r[0]:
                best_r = (key, (rx, ry))
        score = (best_r[0][0], best_r[0][1], best_r[0][2])
        # tie-break by opponent separation then lexicographic dx,dy for determinism
        sep = man(nx, ny, ox, oy)
        cand = (score[0], score[1], score[2], sep, -dx, -dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]