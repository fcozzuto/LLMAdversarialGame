def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Opponent archetype: go to its nearest resource; treat that as its target.
    opp_target = min(resources, key=lambda r: md(ox, oy, r[0], r[1]))
    tx, ty = opp_target[0], opp_target[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    # Extra preference: keep moving toward resources we are close to, but primarily deny opponent's target.
    our_nearest = min(resources, key=lambda r: md(sx, sy, r[0], r[1]))
    nx0, ny0 = our_nearest[0], our_nearest[1]
    cur_near_d = md(sx, sy, nx0, ny0)

    # Use deterministic ordering for ties: smaller dx, then smaller dy.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue

        our_d_t = md(nx, ny, tx, ty)
        opp_d_t = md(ox, oy, tx, ty)

        # Denial margin: positive means we are closer than opponent to the opponent's target.
        denial = (opp_d_t - our_d_t)

        # Secondary objective: reduce our distance to our nearest resource (to avoid stalling).
        our_near_d = md(nx, ny, nx0, ny0)
        progress = (cur_near_d - our_near_d)

        # Tertiary objective: avoid moving away from the board center (stability).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        score = 3.0 * denial + 0.8 * progress + 0.02 * center

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]