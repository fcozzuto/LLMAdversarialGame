def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        move_score = 0.0

        if resources:
            # Pick resource with best advantage: closer to us, farther from opponent
            tgt_score = None
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # reward reaching now, penalize giving opponent advantage
                s = ds - 0.6 * do
                if tgt_score is None or s < tgt_score:
                    tgt_score = s
            # If multiple options, strongly prefer minimizing tgt_score
            move_score = -tgt_score
        else:
            # No visible resources: head to center
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dc = cheb(nx, ny, cx, cy)
            move_score = -dc

        # Soft opponent response: avoid letting opponent get closer next move
        d_opp_now = cheb(nx, ny, ox, oy)
        move_score -= 0.05 * d_opp_now

        if best is None or move_score > best[0]:
            best = (move_score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]