def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obstacles]
    if not res:
        return [0, 0]

    best_move = [0, 0]
    best_score = -10**9

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Score: pick move that maximizes advantage to the "best" contested resource.
        # Add mild preference for reducing our distance to avoid wasting turns.
        move_score = -10**9
        min_self_to_that = 10**9
        for rx, ry in res:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            # Encourage immediate collection (sd==0) and strong advantage; penalize farther goals.
            s = adv * 100 - sd
            if s > move_score or (s == move_score and sd < min_self_to_that):
                move_score = s
                min_self_to_that = sd

        # Additional small tie-break: if opponent is closer overall, avoid moves that keep sd large.
        # (Use global best advantage from current cell as a reference.)
        cur_adv = -10**9
        for rx, ry in res:
            cur_adv = max(cur_adv, (dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry)))
        if move_score < cur_adv - 5:
            move_score -= 25

        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]

    return best_move