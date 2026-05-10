def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Chebyshev distance matches 8-neighborhood diagonal moves
    def cd(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    resset = set(resources)
    # Immediate pickup if possible
    for dx, dy in legal:
        if (sx + dx, sy + dy) in resset:
            return [dx, dy]

    # If game is late, just go for closest resource
    turns_remaining = observation.get("turns_remaining", 0)
    late = turns_remaining is not None and turns_remaining <= 6

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        val = 0
        # Prefer targets we reach strictly sooner than opponent; otherwise reduce value
        for tx, ty in resources:
            myd = cd(nx, ny, tx, ty)
            opd = cd(ox, oy, tx, ty)
            # Score proxy: we want opponent to be slower; tie breaks by points, so ties get smaller bonus
            margin = opd - myd
            if late:
                tval = -myd
            else:
                # Encourage taking unique leads; penalize contested/tied aggressively
                if margin > 0:
                    tval = 1000 + 10 * margin - myd
                elif margin == 0:
                    tval = 200 - 5 * myd
                else:
                    tval = -200 + 2 * margin - myd
            # Small deterministic preference to reduce thrashing: closer to center of resources set
            tval -= 0.01 * (cd(nx, ny, tx, ty))
            if tval > val:
                val = tval
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]