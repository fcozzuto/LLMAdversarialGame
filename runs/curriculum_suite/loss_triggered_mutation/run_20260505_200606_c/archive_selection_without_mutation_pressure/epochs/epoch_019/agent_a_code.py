def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best = (0, 0)
    best_val = -10**18

    # Precompute best/worst distances for opponent to current resources
    opp_dists = []
    for rx, ry in resources:
        if 0 <= rx < w and 0 <= ry < h:
            opp_dists.append((man(ox, oy, rx, ry), rx, ry))
    if not opp_dists:
        return [0, 0]
    opp_dists.sort(key=lambda t: t[0])
    opp_best_d = opp_dists[0][0]
    opp_best_targets = [(d, rx, ry) for (d, rx, ry) in opp_dists if d == opp_best_d]

    # Main heuristic: maximize lead on best target while reducing opponent advantage and matching target row.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        our_best = 10**9
        our_best_targets = []
        for rx, ry in resources:
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                d = man(nx, ny, rx, ry)
                if d < our_best:
                    our_best = d
                    our_best_targets = [(rx, ry)]
                elif d == our_best:
                    our_best_targets.append((rx, ry))
        if our_best == 10**9:
            continue

        # Opponent advantage estimate: how much closer opponent is to some resource than we are.
        # Use opponent's closest resource(s), and also penalize if we move toward resources opponent is already targeting.
        d_opp_closest = 10**9
        row_gap = 0
        # Find closest resource among opponent's best targets
        for _, rx, ry in opp_best_targets:
            d = man(nx, ny, rx, ry)
            if d < d_opp_closest:
                d_opp_closest = d
                row_gap = abs(ny - ry)

        # Lead term: bigger is better.
        lead = opp_best_d - our_best

        # Row-matching (denier): keep near the opponent's best-target row to contest pickups along the sweep.
        if row_gap == 0:
            row_score = 9
        elif row_gap == 1:
            row_score = 5
        elif row_gap == 2:
            row_score = 2
        else:
            row_score = 0

        # Soft penalty for moving away from opponent's closest-resource "lane"
        lane_penalty = d_opp_closest * 0.3

        # Obstacle-aware discouragement: avoid staying in place if there exists any improving move
        stay_penalty = 0.8 if (dx == 0 and dy == 0) else 0.0

        val = lead * 10 + row_score - lane_penalty - stay_penalty

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]