def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = list(observation.get("resources", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if not resources:
        tx, ty = int(round(cx)), int(round(cy))
        best = None
        bestd = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
                if bestd is None or d < bestd:
                    bestd, best = d, (dx, dy)
        return list(best if best is not None else (0, 0))

    # Choose target resource deterministically: prefer those where we're not farther than opponent; then closest self.
    scored_targets = []
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # priority: self can compete (sd <= od), then minimize sd, then deterministic tie by coordinates
        pri = 0 if sd <= od else 1
        scored_targets.append((pri, sd, ry, rx))
    scored_targets.sort()
    _, _, _, tx = scored_targets[0][0], scored_targets[0][1], scored_targets[0][2], scored_targets[0][3]
    target_x, target_y = scored_targets[0][3], scored_targets[0][2]

    # Move: maximize progress toward target, with slight preference to reduce opponent options.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = (nx - target_x) * (nx - target_x) + (ny - target_y) * (ny - target_y)
        self_closest = nd
        # Opponent proximity to same target (to discourage obvious races)
        opp_d = (ox - target_x) * (ox - target_x) + (oy - target_y) * (oy - target_y)
        # If we can reach faster than opponent would, boost.
        win_boost = 0
        if self_closest <= opp_d:
            win_boost = -10
        # Tie-breaker favors staying deterministic: prefer moves closer to target, then lower dx,dy lexicographic.
        score = win_boost - self_closest
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]