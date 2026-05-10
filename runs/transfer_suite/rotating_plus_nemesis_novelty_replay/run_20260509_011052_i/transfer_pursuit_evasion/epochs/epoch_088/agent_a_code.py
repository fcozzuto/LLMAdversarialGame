def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # If can step onto opponent directly, do it (capture radius 0).
    dx0 = ox - sx
    dy0 = oy - sy
    if max(abs(dx0), abs(dy0)) <= 1:
        mdx = 0 if dx0 == 0 else (1 if dx0 > 0 else -1)
        mdy = 0 if dy0 == 0 else (1 if dy0 > 0 else -1)
        nx, ny = sx + mdx, sy + mdy
        if valid(nx, ny):
            return [mdx, mdy]

    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        # Second objective: as pursuer, move toward center to limit zigzag escapes around corners;
        # as evader, move away from center.
        center_dist = cheb(nx, ny, int(round(cx)), int(round(cy)))

        # Third objective: avoid stepping adjacent to obstacles when tie-breaking.
        adj_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_block += 1

        # Deterministic lexicographic scoring:
        if is_pursuer:
            score = (d, center_dist, -adj_block, nx, ny)
            want_min = True
        else:
            score = (-d, -center_dist, -adj_block, nx, ny)
            want_min = False

        if best_score is None or (want_min and score < best_score) or ((not want_min) and score > best_score):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]