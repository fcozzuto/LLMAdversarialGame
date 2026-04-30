def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # No resources: maximize distance from opponent while not hitting obstacles
        best = (None, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = (abs(nx - ox) + abs(ny - oy))
                if score > best[1]:
                    best = ((dx, dy), score)
        return list(best[0]) if best[0] is not None else [0, 0]

    def manh(a, b, c, d): 
        return abs(a - c) + abs(b - d)

    # Choose a contested resource (pivot away from purely self-first targeting).
    # Lower score is better: try to intercept resources the opponent is likely to reach soon.
    best_res = None
    best_rs = 10**9
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Intercept bias: prefer resources that are close to either agent, and where we aren't massively behind.
        rs = (ds + 1) - 0.55 * do
        if rs < best_rs:
            best_rs = rs
            best_res = (rx, ry)

    tx, ty = best_res
    cur_to_t = manh(sx, sy, tx, ty)
    opp_dist = manh(sx, sy, ox, oy)

    best_move = (0, 0)
    best_score = -10**18
    any_valid = False

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        any_valid = True
        nt = manh(nx, ny, tx, ty)
        no = manh(nx, ny, ox, oy)
        # Prefer moving closer to target; also keep/extend distance from opponent to reduce interference.
        closer = cur_to_t - nt
        score = 200 * closer + 3 * no
        # Slight preference for staying within grid and not oscillating: penalize moves that don't help.
        if nt >= cur_to_t:
            score -= 25
        # Encourage stepping onto target tile if adjacent.
        if nt == 0:
            score += 500
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if any_valid:
        return [int(best_move[0]), int(best_move[1])]

    # If all moves blocked by obstacles, try staying.
    return [0, 0]