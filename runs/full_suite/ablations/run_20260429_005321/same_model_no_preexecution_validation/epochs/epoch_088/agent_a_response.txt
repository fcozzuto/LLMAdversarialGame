def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation["resources"] or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation["obstacles"] or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def adj_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    def target_value(px, py):
        if not resources:
            # Drift toward opponent side but keep distance.
            tx = w - 1 if ox < w / 2 else 0
            ty = h - 1 if oy < h / 2 else 0
            dme = cheb(px, py, tx, ty)
            dop = cheb(ox, oy, tx, ty)
            return (dop - dme) * 2.0 - dme - 0.5 * adj_obs(px, py)

        best = -10**18
        for (rx, ry) in resources:
            dme = cheb(px, py, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # Main: pick resources we can beat the opponent to; secondary: avoid being too close to opponent.
            v = (dop - dme) * 6.0 - dme * 0.9 - 0.7 * adj_obs(rx, ry)
            if dme < dop:
                v += 4.0
            # If opponent is extremely close to the same resource, prefer "intercept" by moving toward it less.
            if dop <= 1:
                v -= 3.0
            # Avoid target that puts us next to opponent (risk contest loss).
            v -= 1.2 * (1 if cheb(px, py, ox, oy) <= 1 else 0)
            if v > best: best = v
        return best

    # One-step lookahead: evaluate moves by their resulting best target value.
    best_move = (0, 0); best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        # Penalize moves that end adjacent to obstacles slightly; encourage advancing on winning targets.
        score = target_value(nx, ny) - 0.25 * adj_obs(nx, ny)
        # Tie-break deterministically: prefer staying if equal? We'll prefer smaller |dx| then smaller |dy|.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            def key(m):
                mdx, mdy = m
                return (abs(mdx), abs(mdy), mdx, mdy)
            if key((dx, dy)) < key(best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]