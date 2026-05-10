def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    # One-step lookahead: opponent moves to optimize their goal vs our tentative move.
    best_move = (0, 0)
    if is_evader:
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Opponent (pursuer) chooses move minimizing our distance.
            worst_for_us = 10**9
            for pdx, pdy in moves:
                px, py = ox + pdx, oy + pdy
                if not ok(px, py):
                    continue
                d = cheb(nx, ny, px, py)
                if d < worst_for_us:
                    worst_for_us = d
            # Evader score proxy: maximize resulting distance, and add slight preference to avoid corner traps by spreading.
            val = worst_for_us + 0.01 * cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        best_val = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Opponent (evader) chooses move maximizing distance.
            best_for_opp = -1
            for edx, edy in moves:
                ex, ey = ox + edx, oy + edy
                if not ok(ex, ey):
                    continue
                d = cheb(nx, ny, ex, ey)
                if d > best_for_opp:
                    best_for_opp = d
            # Pursuer score proxy: minimize resulting distance (after opponent response).
            val = best_for_opp
            if val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]