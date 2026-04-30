def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pref_val(rx, ry):
        # Bias toward the "forward" half of the board relative to the opponent.
        if (sx > ox and sy > oy) or (sx < ox and sy < oy):
            return rx + ry if (sx > ox) == (sy > oy) else -(rx + ry)
        return rx - ry if (sx > ox) else (ry - rx)

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # New deterministic fallback: drift toward the board corner that is farthest from the opponent.
        best = None
        for dx, dy, nx, ny in legal:
            corner_score = cheb(nx, ny, 0 if sx > ox else w - 1, 0 if sy > oy else h - 1)
            opp_close = -cheb(nx, ny, ox, oy)
            k = (opp_close, corner_score, dx, dy)
            if best is None or k > best[0]:
                best = (k, dx, dy)
        return [best[1], best[2]]

    # Materially different from pure target-first: for each move, maximize immediate "arrival lead"
    # over the opponent, with an additional obstacle-agnostic pursuit bias and tie-breaking.
    best = None
    best_i = -1
    for dx, dy, nx, ny in legal:
        best_key = None
        for i, (rx, ry) in enumerate(resources):
            if (rx, ry) in obst:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we arrive earlier or same
            finish = -ds
            bias = pref_val(rx, ry)  # deterministic forward bias
            # Penalize moving away from the current-best region by discouraging large ds.
            key = (lead, finish, bias, -abs((rx - nx)) - abs((ry - ny)), -i)
            if best_key is None or key > best_key:
                best_key = key
        if best_key is None:
            best_key = (-999, 0, 0, 0, 0)
        # Prefer the move that best improves (lead, finish) deterministically.
        k2 = (best_key, dx, dy, nx, ny)
        if best is None or k2 > best:
            best = k2
            best_i = 0
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]