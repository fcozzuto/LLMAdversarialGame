def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) or ("pursuer" in self_role and "evader" in opp_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18 if evader else -10**18

    # Deterministic ordering / tie-breaker: fixed preference.
    # Prefer staying when tied for evader, and moving closer for pursuer.
    pref_evader = [(0, 0), (0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    pref_pursuer = [(0, 0), (0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    order = pref_evader if evader else pref_pursuer

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; emulate deterministically
        dist = abs(nx - ox) + abs(ny - oy)

        # One-step lookahead: if our evasion doesn't increase, try to reduce opponent's likely chase.
        # Since opponent policy unknown, approximate by measuring closeness after our move.
        if evader:
            # Maximize distance; slight bias to move to farther corner (stable gradient).
            corner_bias = max(0, (nx in (0, w - 1)) + (ny in (0, h - 1)))
            score = dist * 100 + corner_bias
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # Pursuer: minimize distance; avoid moves that would be "blocked" (already handled by inside).
            corner_bias = (nx in (0, w - 1)) + (ny in (0, h - 1))
            score = -(dist * 100 + corner_bias * 0)  # keep simple and stable
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]