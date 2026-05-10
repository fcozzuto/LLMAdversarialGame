def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    options = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def min_dist_to_opp(x, y):
        d = manh(x, y, ox, oy)
        for (tx, ty) in opp_t:
            dd = abs(tx - x) + abs(ty - y)
            if dd < d:
                d = dd
        return d

    # Pick a frontier-avoiding target: far from opponent territory, yet not too far from us.
    if unclaimed:
        best = unclaimed[0]
        best_val = -10**18
        limit = 32 if len(unclaimed) > 32 else len(unclaimed)
        for i in range(limit):
            x, y = unclaimed[i]
            val = min_dist_to_opp(x, y) - 0.6 * manh(sx, sy, x, y)
            if val > best_val:
                best_val = val
                best = (x, y)
        tx, ty = best
        # Try stepping toward the target; if blocked, fall back to best local move.
        pref = None
        for dx, dy in options:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            # Encourage progress to target; discourage moving into opponent territory if we can avoid it.
            score = -manh(nx, ny, tx, ty) + 0.15 * min_dist_to_opp(nx, ny)
            if (nx, ny) in opp_t:
                score -= 2.5
            if (nx, ny) in set(map(tuple, unclaimed)) if unclaimed else False:
                score += 3.0
            if pref is None or score > pref[0]:
                pref = [score, dx, dy]
        if pref is not None:
            return [pref[1], pref[2]]
    else:
        # No unclaimed: maintain distance from opponent and maneuver around obstacles.
        best = None
        for dx, dy in options:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            score = 0.8 * min_dist_to_opp(nx, ny) - 0.1 * manh(nx, ny, ox, oy)
            if (nx, ny) in opp_t:
                score -= 1.0
            if best is None or score > best:
                best = score
                best_move = [dx, dy]
        if best is not None:
            return best_move

    return [0, 0]