def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def role_is_purs(role):
        r = (role or "").lower()
        if "purs" in r:
            return True
        if "evad" in r:
            return False
        return None

    sr = role_is_purs(observation.get("self_role"))
    orr = role_is_purs(observation.get("opponent_role"))
    if sr is None:
        sr = (orr is False)
    is_pursuer = bool(sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Predict opponent next position under direct pursuit (if opponent is pursuer), else assume it moves directly away (if opponent is evader).
    def opp_next(px, py):
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                continue
            ddx, ddy = nx - ox, ny - oy
            d2 = ddx * ddx + ddy * ddy
            if orr is True:  # opponent pursuer -> minimize distance to us (current self pos)
                v = -d2
            elif orr is False:  # opponent evader -> maximize distance from us
                v = d2
            else:
                v = -d2
            if best is None or v > bestv or (v == bestv and (dx, dy) < best):
                best, bestv = (dx, dy), v
        if best is None:
            return px, py
        return px + best[0], py + best[1]

    # Score our candidate move.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dxo, dyo = nx - ox, ny - oy
        d2 = dxo * dxo + dyo * dyo
        if is_pursuer:
            score = -d2
            # Small bonus for moving along dominant axis to reduce capture time against direct pursuit.
            score += -((abs(nx - ox) > abs(ny - oy)) * 0.01)
        else:
            # Evader: maximize current distance plus distance from where the opponent will likely move next.
            nx2, ny2 = opp_next(ox, oy)
            ddx2, ddy2 = nx - nx2, ny - ny2
            d2_future = ddx2 * ddx2 + ddy2 * ddy2
            score = d2 * 1.0 + d2_future * 0.6

            # Avoid self-cornering: if move reduces distance to the nearest wall without increasing chase distance, penalize slightly.
            dist_wall = min(nx, ny, w - 1 - nx, h - 1 - ny)
            dist_wall_now = min(sx, sy, w - 1 - sx, h - 1 - sy)
            if dist_wall < dist_wall_now and d2 < (sx - ox) ** 2 + (sy - oy) ** 2:
                score -= 0.2

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]