def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    for r in resources:
        if (sx, sy) == (r[0], r[1]):
            return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Prioritize: take resources when we are closer; if opponent is closer, choose moves that reduce their lead.
    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not valid(nx, ny):
            continue

        score = 0
        # Small tie-break to avoid oscillation: prefer moves that generally go toward center early, away late.
        center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
        t = observation.get("turns_remaining", 0)
        center_bias = (1.0 if t > (w * h) // 2 else -1.0)

        score += center_bias * (-((nx - center_x) ** 2 + (ny - center_y) ** 2)) * 1e-4

        for rx, ry in resources:
            myd = cheb(rx, ry, nx, ny)
            opd = cheb(rx, ry, ox, oy)

            if myd == 0:
                score += 1_000_000

            # Favor resources where we would be at least as close as opponent.
            if myd <= opd:
                lead = opd - myd  # bigger lead = better
                score += 5000 / (1 + myd) + 1200 * lead
            else:
                # If opponent is closer, discourage; but allow if we can reduce their lead quickly.
                diff = myd - opd  # smaller diff = better
                score -= 2500 * (1 / (1 + myd)) * (1 + diff)
                # Encourage decreasing their lead this turn.
                cur_myd = cheb(rx, ry, sx, sy)
                cur_diff = cur_myd - opd
                if diff < cur_diff:
                    score += 900 * (cur_diff - diff)

        if score > best_score:
            best_score = score
            best_move = (dxi, dyi)

    return [int(best_move[0]), int(best_move[1])]