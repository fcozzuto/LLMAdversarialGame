def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target that we are currently at least as fast for (otherwise maximize our gap).
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        faster = ds <= do
        # key: faster-first, then smaller ds, then larger do
        key = (0 if faster else 1, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    rx, ry = best_t

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        self_to_t = cheb(nx, ny, rx, ry)
        opp_to_t = cheb(ox, oy, rx, ry)
        self_to_o = cheb(nx, ny, ox, oy)

        # If we can race to the target, push hard; otherwise improve our relative gap and stay safe.
        rel = opp_to_t - self_to_t
        score = rel * 10 - self_to_t + self_to_o * 0.5

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]