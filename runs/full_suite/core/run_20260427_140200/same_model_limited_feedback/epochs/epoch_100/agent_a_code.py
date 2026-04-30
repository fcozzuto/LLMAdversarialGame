def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d): 
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_sc = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                sc = -10**9
            else:
                ddx = nx - tx
                ddy = ny - ty
                if ddx < 0: ddx = -ddx
                if ddy < 0: ddy = -ddy
                sc = -(ddx if ddx > ddy else ddy)
            if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
                best_sc, best = sc, (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            score = -10**9
        else:
            # Race heuristic: prefer targets where opponent is relatively farther.
            best_race = -10**9
            best_selfd = 10**9
            for rx, ry in resources:
                selfd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                race = oppd - selfd
                if race > best_race or (race == best_race and selfd < best_selfd):
                    best_race = race
                    best_selfd = selfd
            # Tie-break by moving closer overall and slightly away from obstacles.
            penalty = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    ax, ay = nx + adx, ny + ady
                    if (ax, ay) in obs:
                        penalty += 1
            score = best_race * 10 - best_selfd - penalty
            # If opponent is about to land on the same resource, don't be directly adjacent to them unnecessarily.
            if cheb(nx, ny, ox, oy) <= 1:
                score -= 0.5
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]