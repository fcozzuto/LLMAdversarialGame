def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose target: first prefer resources we can reach no later than opponent (earliest),
    # else pick resource maximizing relative advantage (opponent farther than us).
    best = None
    for rx, ry in resources:
        sd = md(x, y, rx, ry)
        od = md(ox, oy, rx, ry)
        if sd <= od:
            key = (0, sd, od, rx, ry)  # can beat: earlier self wins
        else:
            key = (1, -(od - sd), sd, rx, ry)  # cannot beat: maximize gap
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Assume opponent greedily moves toward same target.
    def opp_next_dist():
        bestd = None
        for pdx, pdy in moves:
            nx, ny = ox + pdx, oy + pdy
            if not inb(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd = d
        if bestd is None:
            return md(ox, oy, tx, ty)
        return bestd

    oppd_next = opp_next_dist()

    # Evaluate our candidate moves by resulting distance difference against opponent.
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        selfd = md(nx, ny, tx, ty)
        # maximize (oppd_next - selfd); tie-break: smaller selfd, then prefer diagonal/forward deterministically
        score = (oppd_next - selfd, -selfd, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move