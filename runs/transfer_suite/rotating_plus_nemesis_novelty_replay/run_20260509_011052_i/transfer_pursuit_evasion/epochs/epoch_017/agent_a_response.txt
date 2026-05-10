def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Predict evader's greedy step toward its nearest boundary corner (wall-run).
    near_left = ox
    near_right = (w - 1) - ox
    near_top = oy
    near_bottom = (h - 1) - oy
    bx = 0 if near_left <= near_right else (w - 1)
    by = 0 if near_top <= near_bottom else (h - 1)
    goal_corner = (bx, by)

    pred = (ox, oy)
    bestg = 10**9
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if not inside(nx, ny):
            continue
        d = max(abs(nx - goal_corner[0]), abs(ny - goal_corner[1]))
        if d < bestg:
            bestg = d
            pred = (nx, ny)

    px, py = pred

    # Interception: aim to minimize distance to predicted position and cut off toward goal.
    def score_move(nx, ny):
        d_pred = max(abs(nx - px), abs(ny - py))
        # Encourage approaching the same "escape line" toward the goal corner.
        # If goal is vertical wall, align x; if horizontal, align y; else align both.
        align = 0
        align += 0 if goal_corner[0] == nx else 1
        align += 0 if goal_corner[1] == ny else 1
        # Extra: prefer moves that reduce distance to the goal corner overall.
        d_goal = max(abs(nx - goal_corner[0]), abs(ny - goal_corner[1]))
        # Mild obstacle/edge safety: avoid corners far from predicted approach.
        edge = min(nx, (w - 1) - nx, ny, (h - 1) - ny)
        return d_pred * 10 - align * 2 + d_goal - edge * 0.01

    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = score_move(nx, ny)
        if sc < best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]