def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose target using "can-win first" policy: prefer resources where I'm not farther than opponent,
    # otherwise pick resource with largest contest advantage (opponent farther).
    best = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        winish = 1 if myd <= opd else 0
        # Time pressure: later game weight distance more, early weight contest more.
        tr = observation.get("turns_remaining", 1)
        time_factor = 0.15 + 0.85 * (min(max(tr, 0), 50) / 50.0)
        # Slight preference away from obstacles adjacency to reduce accidental traps.
        adj = 0
        for ax, ay in ((rx-1, ry), (rx+1, ry), (rx, ry-1), (rx, ry+1)):
            if (ax, ay) in obstacles:
                adj += 1
        score = (winish * 1000) + (opd - myd) * (1.2 if tr > 10 else 0.7) + (-myd) * (1.0 * (1 - time_factor) + 0.3) - adj * 0.5
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Avoid stepping adjacent to obstacles (soft).
        near_obs = 0
        for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx-1, ny+1), (nx+1, ny-1), (nx+1, ny+1)):
            if (ax, ay) in obstacles:
                near_obs += 1
        myd2 = man(nx, ny, tx, ty)
        opd2 = man(ox, oy, tx, ty)
        # Block/contest: prefer moves that make me at least as close as opponent to the chosen target.
        contest = 1.0 if myd2 <= opd2 else 0.0
        # Also prefer immediate reduction in distance to target.
        reduce = -myd2
        # If I can grab a resource immediately, prioritize that.
        grab = 1.5 if (nx, ny) in resources else 0.0
        sc = (contest * 500) + grab * 50 + reduce * (2.0 if observation.get("turns_remaining", 1) <= 10 else 1.3) - near_obs * 0.8
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]