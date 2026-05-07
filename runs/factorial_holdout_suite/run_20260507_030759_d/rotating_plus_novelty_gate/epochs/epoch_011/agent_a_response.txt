def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        # Drift to reduce distance to opponent row sweep: aim to match opponent x, then approach opponent
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # Prefer moving toward opponent's x (deterministic), then y
            key = (abs(nx - ox), abs(ny - oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Lookahead-1: choose move that maximizes best-case "we can secure before opponent" slack.
    # Slack = opp_dist - our_dist (larger is better for us). Tie-break by smaller our_dist, then stable.
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_slack = None
        best_our = None
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in obstacles:
                continue
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            slack = opp_d - our_d
            if best_slack is None or slack > best_slack or (slack == best_slack and our_d < best_our):
                best_slack = slack
                best_our = our_d
        # Prefer positive slack; if all negative, pick least negative (closest contest)
        # Key sorts ascending, so use negative slack.
        key = (-best_slack, best_our, abs((nx - rx) if resources else 0), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]