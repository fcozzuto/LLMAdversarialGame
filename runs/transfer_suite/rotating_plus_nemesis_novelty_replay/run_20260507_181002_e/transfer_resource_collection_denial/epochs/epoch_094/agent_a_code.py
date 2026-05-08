def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Prefer moves that make us strictly closer to a resource than opponent, otherwise slow their progress.
    best = (-(10**18), 0, 0)  # (value, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Evaluate best "swing" resource for this next position
        # Tie-break deterministically by consistent ordering.
        best_local = -(10**18)
        for (rx, ry) in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # If we can reach sooner, gain strongly; if not, reduce the opponent advantage.
            # Also slightly prefer reducing our distance overall.
            val = 0
            if d_self < d_opp:
                val += 1000 - 10 * d_self + (d_opp - d_self) * 5
            else:
                val += - (10 * (d_self - d_opp) + d_self)  # penalize falling behind
                val += 2 if d_self == d_opp else 0
            # Small deterministic preference: target closer in absolute terms when values tie
            val -= 0.001 * d_self
            if val > best_local:
                best_local = val

        # Secondary: if we can collect immediately, ensure that dominates
        immediate = 1 if (nx, ny) in resources else 0
        val2 = best_local + 100000 * immediate
        if (val2, dx, dy) > (best[0], best[1], best[2]):
            best = (val2, dx, dy)

    return [int(best[1]), int(best[2])]