def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Predict opponent likely target: nearest by Chebyshev distance.
    best_t = None
    best_od = 10**9
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < best_od or (d == best_od and (rx, ry) < best_t):
            best_od = d
            best_t = (rx, ry)

    tx, ty = best_t
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Value: how much closer we get than opponent to some resource.
        max_gap = -10**18
        best_my = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            gap = opd - myd  # positive means we are effectively nearer to contest
            if gap > max_gap:
                max_gap = gap
            if myd < best_my:
                best_my = myd

        # Additional pressure: prioritize beating the predicted opponent target.
        my_to_target = cheb(nx, ny, tx, ty)
        opp_to_target = cheb(ox, oy, tx, ty)
        target_gap = opp_to_target - my_to_target

        # If opponent can reach the target quickly, strongly prefer intercepting it.
        val = max_gap * 10 + target_gap * 4

        # Discourage stepping away from the predicted target if already best competitor.
        cur_my_to_target = cheb(sx, sy, tx, ty)
        if target_gap > 0 and my_to_target > cur_my_to_target:
            val -= 6

        # Deterministic tie-break: prefer smallest (dx,dy) lexicographically after better val.
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move