def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            # Deterministic race heuristic: maximize lead over opponent; break ties by reaching sooner.
            best_race_for_this_move = -10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                race = oppd - myd
                # Slight bias to avoid "trading" resources that are not worth it.
                score = race * 1000 - myd
                if score > best_race_for_this_move:
                    best_race_for_this_move = score
            score = best_race_for_this_move

        else:
            # No visible resources: drift toward center to reduce worst-case distance.
            distc = abs(nx - cx) + abs(ny - cy)
            score = -distc

        # Prefer moves that also reduce distance to opponent if race is close (strategic pressure).
        if resources:
            score += -0.01 * cheb(nx, ny, ox, oy)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]