def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    self_role = observation.get("self_role", "pursuer")
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                moves.append((dx, dy))

    pursuer = (str(self_role).lower().find("purs") != -1)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if pursuer:
        # Target the opponent, but prefer moves that also reduce distance to any corner to avoid dead-ends.
        best_corner = max(corners, key=lambda c: dist2(sx, sy, c[0], c[1]))
        corner_weight = -0.02
    else:
        # Evader: maximize distance from pursuer; also head to the farthest corner.
        best_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        corner_weight = 0.06

    best_move = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        # Determine progress relative to current state (helps avoid dithering).
        d_cur = dist2(sx, sy, ox, oy)
        progress = d_cur - d_opp  # positive if closer

        # Bias toward moving in the general direction to/from the opponent.
        signx = 0 if ox == sx else (1 if ox > sx else -1)
        signy = 0 if oy == sy else (1 if oy > sy else -1)
        align = (1 if dx == signx else 0) + (1 if dy == signy else 0)

        # Obstacle proximity penalty (deterministic local look).
        prox_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obs:
                    prox_pen += 1

        # Corner bias.
        corner_bias = dist2(nx, ny, best_corner[0], best_corner[1])

        if pursuer:
            # Lower distance wins; use progress to encourage true closing.
            score = -d_opp + 0.08 * progress + 0.015 * align + corner_weight * corner_bias - 0.12 * prox_pen
            if best_score is None or score > best_score:
                best_score, best_move = score, [dx, dy]
        else:
            # Higher distance wins.
            score = d_opp - 0.06 * progress + 0.02 * align + corner_weight * corner_bias - 0.12 * prox_pen
            if best_score is None or score > best_score:
                best_score, best_move = score, [dx, dy]

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]