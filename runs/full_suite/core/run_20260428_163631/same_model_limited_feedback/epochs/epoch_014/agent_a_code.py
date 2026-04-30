def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        self_target = min(resources, key=lambda r: dist((sx, sy), r))
        opp_target = min(resources, key=lambda r: dist((ox, oy), r))
    else:
        self_target = (sx, sy)
        opp_target = (ox, oy)

    best = None
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx
            ny = sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            ds = dist((nx, ny), self_target)
            do = dist((nx, ny), (ox, oy))
            dp = dist((nx, ny), opp_target)

            # Primary: get closer to our target; Secondary: keep away from opponent; Tertiary: avoid giving opponent access
            score = -ds + 0.15 * do - 0.05 * dp

            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]
            elif score == best_score:
                # Deterministic tie-break: prefer moves that reduce our distance, then prefer (dx,dy) ordering
                cur_ds = dist((sx + best[0], sy + best[1]), self_target)
                if ds < cur_ds or (ds == cur_ds and (dx, dy) < (best[0], best[1])):
                    best = [dx, dy]

    if best is None:
        return [0, 0]
    return best