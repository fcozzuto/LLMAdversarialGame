def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        axd = abs(dx)
        ayd = abs(dy)
        return axd if axd > ayd else ayd

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Opponent: for any cell, best distance it can achieve next turn (one move) to a target.
    def opp_best_dist(tx, ty):
        best = 10**9
        for mdx, mdy in moves:
            nx, ny = ox + mdx, oy + mdy
            if inb(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < best:
                    best = d
        return best if best != 10**9 else cheb(ox, oy, tx, ty)

    # Choose our move by maximizing guaranteed/likely race advantage (2-step-ish heuristic).
    best_move = (0, 0)
    best_val = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue

        val = 0
        # If we can collect immediately, prioritize strongly.
        if (nx, ny) in [tuple(r) for r in resources]:
            val += 1000

        # Race heuristic: pick resource that maximizes (opp can’t beat us next; plus we approach it)
        # If we can reach in 2 moves (current+one more), give extra weight.
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_own = cheb(nx, ny, rx, ry)
            # Our next move might also help; approximate by allowing one more step.
            # If d_own <= 1 then we are effectively on/next to it (2-ply capture).
            d_opp = opp_best_dist(rx, ry)
            race = d_opp - d_own
            capture_bonus = 200 if d_own <= 1 else (50 if d_own == 2 else 0)
            denom = cheb(nx, ny, rx, ry) + 1
            approach = 10 / denom
            score = race * 20 + capture_bonus + approach
            # Tie-break: prefer increasing separation if racing is similar
            opp_sep = cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)
            score += 2 * (1 if opp_sep > 0 else 0)
            if score > local_best:
                local_best = score
        val += local_best

        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]