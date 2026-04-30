def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append([dx, dy])

    if not resources or not moves:
        return [0, 0]

    def cheb(a, b, c, d):
        adx = a - c
        if adx < 0:
            adx = -adx
        ady = b - d
        if ady < 0:
            ady = -ady
        return adx if adx >= ady else ady

    best_move = moves[0]
    best_score = -10**9

    # Prefer routes that create advantage over the opponent on the most "contested" resources.
    # Score = advantage-to-target - small distance-to-support - obstacle avoidance (already filtered).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        move_score = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # advantage: closer to resource than opponent
            adv = do - ds
            # slight preference for actually progressing even if not currently advantaged
            progress = -0.08 * ds
            # slight preference for central-ish resources to reduce dead ends
            cent = -0.01 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            s = adv + progress + cent
            if s > move_score:
                move_score = s
        # tie-break deterministically by lexicographic (dx,dy) preference after scoring
        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]
        elif move_score == best_score:
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return best_move