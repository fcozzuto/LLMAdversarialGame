def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        # move to reduce distance to a central-ish point deterministically
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = md(nx, ny, tx, ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Choose move that maximizes guaranteed prospect over opponent for the best contestable resource.
    best_move = (None, None, -10**18)
    for dx, dy, nx, ny in legal:
        my_d0 = md(nx, ny, ox, oy)
        score_here = -10**18
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obstacles:
                continue
            my_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            # If opponent can arrive no later, strongly discourage (resource denial).
            # Else, reward being earlier and closer.
            rel = opp_d - my_d  # positive good
            # Additional tie-break pressure: avoid giving opponent an easy follow-up nearby.
            chase_pen = md(nx, ny, ox, oy) - my_d0  # prefer not increasing distance to opponent too much
            s = 1000 * rel - 3 * my_d - 2 * (1 if rel < 0 else 0) - chase_pen
            if s > score_here:
                score_here = s
        # Small determinism: prefer moves that keep you closer to any resource when prospects tie.
        if score_here > best_move[2]:
            best_move = (dx, dy, score_here)
        elif score_here == best_move[2] and best_move[0] is not None:
            # tie-breaker by lexicographic move order preference: stay, then up/down/left/right, then diagonals
            order = {(0,0):0,(0,1):1,(0,-1):2,(-1,0):3,(1,0):4,(-1,-1):5,(1,-1):6,(-1,1):7,(1,1):8}
            if order[(dx, dy)] < order[(best_move[0], best_move[1])]:
                best_move = (dx, dy, score_here)

    return [int(best_move[0]), int(best_move[1])]