def choose_move(observation):
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    w = observation["grid_width"]
    h = observation["grid_height"]

    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    x, y = self_pos
    # Pick target resource: prefer ones we're closer to than opponent
    best = None
    best_val = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = cheb((x, y), (rx, ry))
        do = cheb(tuple(opp_pos), (rx, ry))
        val = ds - 0.6 * do
        if best is None or val < best_val or (val == best_val and ds < cheb((x, y), tuple(best))):
            best = (rx, ry)
            best_val = val
    if best is None:
        return [0, 0]

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = cheb((nx, ny), best)
        # Tie-breakers: don't let opponent get much closer, and prefer progress
        d_opp = cheb((nx, ny), tuple(opp_pos))
        score = (d_to, d_opp, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]