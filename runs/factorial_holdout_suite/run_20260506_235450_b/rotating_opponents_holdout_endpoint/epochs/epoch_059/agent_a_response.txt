def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        try:
            x, y = int(a[0]), int(a[1])
        except Exception:
            try:
                x, y = int(a.get("x")), int(a.get("y"))
            except Exception:
                continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
        except Exception:
            try:
                x, y = int(r.get("x")), int(r.get("y"))
            except Exception:
                continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_delta = [0, 0]
    best_score = -10**18

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Prefer a resource where we can arrive earlier than the opponent; otherwise, still go for best slack.
        move_best = -10**18
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)

            # If opponent is already as close or closer, discount heavily but not to zero (sometimes still best).
            contest = 1.0 if our_d < opp_d else 0.35
            # Main objective: maximize advantage (opponent distance - our distance), plus slight preference for closeness.
            val = (opp_d - our_d * 1.08) * contest - 0.03 * our_d
            if val > move_best:
                move_best = val

        # Small penalty for proximity to obstacles to reduce collisions with tight obstacle layouts.
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    near_obs += 1
        move_score = move_best - 0.02 * near_obs

        if move_score > best_score:
            best_score = move_score
            best_delta = [dx, dy]

    return best_delta