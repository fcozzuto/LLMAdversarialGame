def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or ("pursuer" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    wall_x = 0 if ox <= 0 else (w - 1 if ox >= w - 1 else None)
    wall_y = 0 if oy <= 0 else (h - 1 if oy >= h - 1 else None)
    near_wall = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)

    best_score = None
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        mdx, mdy = abs(nx - ox), abs(ny - oy)
        dist = mdx + mdy
        boundary = min(nx, w - 1 - nx, ny, h - 1 - ny)
        center = abs(nx - cx) + abs(ny - cy)

        if is_pursuer:
            score = -dist
            score += -0.15 * center
            if near_wall:
                if wall_x is not None:  # opponent pinned left/right: close x first
                    score += -0.6 * mdx
                if wall_y is not None:  # opponent pinned up/down: close y first
                    score += -0.6 * mdy
                # cut off by preferring moves that reduce both axes when possible
                score += -0.05 * (mdx * 0.5 + mdy * 0.5)
        else:
            score = dist
            # avoid getting stuck in walls against a wall-runner
            score += 0.12 * boundary
            # but don't suicide into opponent
            score += -0.03 * center
            # slightly prefer moves that keep line-of-sight in either axis
            score += 0.02 * (mdx + mdy)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]