def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rem = observation.get("turns_remaining", 0)

    # Choose best move by deterministic scoring
    best = (0, 0)
    best_score = -10**18

    # If no resources, drift toward center
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best_score:
                best_score = d
                best = (dx, dy)
        return [best[0], best[1]]

    res = [tuple(r) for r in resources]
    opp_nearest = min(cheb(ox, oy, rx, ry) for rx, ry in res)
    our_nearest = min(cheb(sx, sy, rx, ry) for rx, ry in res)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Find best resource to secure
        best_gain = -10**18
        best_tie = None
        for rx, ry in res:
            d_us = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)

            # Only count if we can realistically arrive before opponent (or tie-break)
            # Tie-break favors points for earlier collection; if equal, prefer smaller combined arrival.
            if rem > 0:
                if d_us > rem:
                    continue

            # Gain: opponent farther than us is good; also prefer quicker arrival.
            # Add tiny deterministic tiebreak using coordinates.
            gain = (d_opp - d_us) * 1000 - d_us
            gain += -(rx + 31 * ry) * 0.000001
            if gain > best_gain:
                best_gain = gain
                best_tie = (rx, ry, d_us, d_opp)

        # If we can't secure anything (e.g., all too far), then race for nearest resource and reduce opponent pressure
        if best_gain == -10**18:
            d_us = min(cheb(nx, ny, rx, ry) for rx, ry in res)
            d_opp2 = min(cheb(ox, oy, rx, ry) for rx, ry in res)
            best_gain = (d_opp2 - d_us) * 1000 - d_us

        # Additional strategic term: avoid moves that let opponent immediately take many turns sooner
        # (proxy by comparing their nearest distance after our move vs ours nearest)
        our_after = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        opp_after = min(cheb(ox, oy, rx, ry) for rx, ry in res)
        safety = (our_after - opp_after) * 2

        # Deterministic tie-break toward higher x then y preference
        move_key = (nx * 10 + ny)

        score = best_gain - safety + move_key * 0.000001

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]