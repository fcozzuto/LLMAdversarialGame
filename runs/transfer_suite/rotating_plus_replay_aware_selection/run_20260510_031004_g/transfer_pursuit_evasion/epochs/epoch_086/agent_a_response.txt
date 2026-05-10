def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                m += 1
        return m

    best = None
    best_score = -10**18 if self_is_pursuer else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        corner_bias = 0
        if not self_is_pursuer:
            md = 10**18
            for cx, cy in corners:
                t = dist2(nx, ny, cx, cy)
                if t < md:
                    md = t
            corner_bias = -md * 0.0001  # keep evader from hugging center when chasing mobility
        else:
            md = 10**18
            for cx, cy in corners:
                t = dist2(nx, ny, cx, cy)
                if t < md:
                    md = t
            corner_bias = -md * 0.0001  # slight regularization

        if self_is_pursuer:
            capture = (nx == ox and ny == oy)
            score = (1e9 if capture else 0) - d + 0.25 * mob + corner_bias
            if score > best_score:
                best_score, best = score, [dx, dy]
        else:
            near_pursuer_pen = -d * 0.5  # stronger repel
            score = d + 0.25 * mob + corner_bias + near_pursuer_pen
            # If by any chance moving onto pursuer (could be capture), heavily penalize
            if nx == ox and ny == oy:
                score -= 1e9
            if score < best_score:
                best_score, best = score, [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]