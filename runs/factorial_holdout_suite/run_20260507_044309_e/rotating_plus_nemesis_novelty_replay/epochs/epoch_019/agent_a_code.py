def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                # allow diagonals and cardinals, but keep within bounds by engine rule
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    moves.append((dx, dy))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer blocking resources on/near opponent's distance shell by strong advantage term.
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue

        opp_row = oy
        self_to = cheb(nx, ny, ox, oy)
        score = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # higher is better: we're closer sooner

            # Deny/pressure: resources on or near opponent's row are more valuable tactically.
            deny = 0.0
            if ry == opp_row:
                deny = 3.0
            elif abs(ry - opp_row) == 1:
                deny = 1.2

            # If we can capture immediately, strongly commit to that.
            immediate = 4.0 if (nx == rx and ny == ry) else 0.0

            # Slight preference for shorter own distance to ensure progress.
            progress = -0.15 * sd

            # Avoid stepping too close to opponent unless it increases advantage (resource race).
            proximity_penalty = -0.05 * self_to if adv < 0 else 0.0

            cand = adv + deny + immediate + progress + proximity_penalty
            if cand > score:
                score = cand

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prefer moves that reduce chebyshev distance to the currently best estimated target
            # by lexicographic order (stable).
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]