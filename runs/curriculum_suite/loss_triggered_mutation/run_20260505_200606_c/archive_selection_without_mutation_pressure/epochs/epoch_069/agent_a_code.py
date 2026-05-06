def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or []) if p is not None and len(p) >= 2}
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0.0
        our_min = 10**9
        opp_min = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_our = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_our < our_min:
                our_min = d_our
            if d_opp < opp_min:
                opp_min = d_opp
            if d_our <= d_opp:
                score += (d_opp - d_our) - 0.1 * d_our
            else:
                score -= 0.05 * d_our
        score += 0.15 * (opp_min - our_min)

        # tie-break: prefer closer to resources and not drifting away from center line
        tie = (-(score), our_min, abs(nx - 3.5) + abs(ny - 3.5), dx, dy)
        if best is None or tie < best:
            best = tie
            best_move = [dx, dy]

    return best_move if best is not None else [0, 0]