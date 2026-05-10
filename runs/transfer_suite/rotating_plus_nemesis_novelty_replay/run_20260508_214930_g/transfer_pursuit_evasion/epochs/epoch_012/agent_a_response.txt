def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            try:
                obs.add((int(b[0]), int(b[1])))
            except:
                pass

    actions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs
    def next_pos(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            return x, y
        return nx, ny

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Direct capture (capture_radius=0): move onto opponent.
    for dx, dy in actions:
        nsx, nsy = next_pos(sx, sy, dx, dy)
        if nsx == ox and nsy == oy:
            return [dx, dy]

    def legal_moves_from(px, py):
        ms = []
        for mdx, mdy in actions:
            nx, ny = next_pos(px, py, mdx, mdy)
            ms.append((mdx, mdy, nx, ny))
        return ms

    our_moves = legal_moves_from(sx, sy)
    opp_moves = legal_moves_from(ox, oy)

    def opp_wall_bias(nx, ny, curx, cury):
        # Encourage "wall-running": favor cells closer to a wall edge when not blocked.
        edges = (nx == 0) or (nx == w - 1) or (ny == 0) or (ny == h - 1)
        md = abs(nx - curx) + abs(ny - cury)
        return (1 if edges else 0) + (0.01 * md)

    best = [0, 0]
    best_score = None
    for dx, dy, nsx, nsy in our_moves:
        # Our objective: minimize opponent's best response distance; also prefer cutting off options.
        opp_best = -1e18
        opp_best_state = (ox, oy)
        for odx, ody, nox, noy in opp_moves:
            d = dist2(nox, noy, nsx, nsy)
            # Opponent tries to maximize distance from our next pos; slight bias to edges.
            opp_score = d + 0.5 * opp_wall_bias(nox, noy, ox, oy)
            if opp_score > opp_best:
                opp_best = opp_score
                opp_best_state = (nox, noy)

        nox, noy = opp_best_state
        d_after = dist2(nox, noy, nsx, nsy)

        # Option-cut heuristic: after our move, assume opponent will land at its best state; then count how constrained it is.
        # Lower distance and lower opponent mobility is good for us.
        opp_mob = 0
        for mdx, mdy in actions:
            tx, ty = next_pos(nox, noy, mdx, mdy)
            if (tx, ty) != (nox, noy) or True:
                if inb(tx, ty) and not blocked(tx, ty):
                    opp_mob += 1
        our_mob = 0
        for mdx, mdy in actions:
            tx, ty = next_pos(nsx, nsy, mdx, mdy)
            if (tx, ty) != (nsx, nsy) or True:
                if inb(tx, ty) and not blocked(tx, ty):
                    our_mob += 1

        score = (-d_after) - 0.08 * opp_mob + 0.02 * our_mob
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best