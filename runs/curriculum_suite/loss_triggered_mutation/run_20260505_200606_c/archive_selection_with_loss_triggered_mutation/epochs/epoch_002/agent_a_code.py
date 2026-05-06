def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    moves.sort()

    # Choose a target resource by maximizing "claim advantage" for us over opponent.
    # Advantage = opponentDist - ourDist (bigger means we likely get it first).
    if resources:
        best_adv = None
        target = None
        for rx, ry in resources:
            our_d = man(sx, sy, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Small bias: prefer closer to reduce variance and encourage progress.
            adv = (opp_d - our_d) * 10 - our_d
            key = (-(adv), rx, ry)  # deterministic min on derived key
            if best_adv is None or key < best_adv:
                best_adv = key
                target = (rx, ry)
        tx, ty = target
    else:
        # If no resources, head to opponent (deterministic, but still legal).
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base: reduce distance to target.
        d_self = man(nx, ny, tx, ty)
        # Compete: how much closer we become than opponent after this move.
        d_opp = man(ox, oy, tx, ty)
        # Obstacle pressure: discourage stepping adjacent to obstacles (risk of getting stuck).
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_obs += 1

        score = 0
        score += 1000 if (nx == tx and ny == ty) else 0
        score += -d_self
        score += (d_opp - d_self)  # larger means more likely to secure
        score += -0.8 * adj_obs

        # Slight deterrent to oscillation: prefer moves that change position unless equal.
        if dx == 0 and dy == 0:
            score -= 0.2

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]