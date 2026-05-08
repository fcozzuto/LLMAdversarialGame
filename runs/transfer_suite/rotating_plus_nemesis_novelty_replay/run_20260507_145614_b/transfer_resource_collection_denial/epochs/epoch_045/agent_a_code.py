def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if any(sx == r[0] and sy == r[1] for r in resources):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        val = 0.0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                val += 1_000_000
            else:
                lead = opd - myd
                if lead > 0:
                    val += 120.0 * lead + 25.0 / (myd + 1)
                else:
                    val -= 90.0 * (-lead) + 8.0 / (myd + 1)
        # small tie-break: prefer moves that reduce distance to best resource we can lead on
        if val == best_val:
            pass

        if val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return best_move