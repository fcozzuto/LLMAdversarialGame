def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position")
    op = observation.get("opponent_position")
    if not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y, a, b):
        dx = abs(x - a)
        dy = abs(y - b)
        return dx if dx > dy else dy

    def mindist_to_obs(x, y):
        if not obstacles:
            return 99
        best = 99
        for (ox2, oy2) in obstacles:
            d = abs(x - ox2) + abs(y - oy2)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d = cheb(nx, ny, ox, oy)
        dist_to_obs = mindist_to_obs(nx, ny)

        # Encourage obstacle-safe motion (both roles)
        safe_bonus = dist_to_obs
        # Encourage moving in direction that continues pursuit/escape along axes
        dir_x = 0 if ox == nx else (1 if ox > nx else -1)
        dir_y = 0 if oy == ny else (1 if oy > ny else -1)
        align = (1 if dx == dir_x else 0) + (1 if dy == dir_y else 0)  # 0..2

        if is_evader:
            # maximize distance; prefer sliding away while staying safe
            score = (d * 10) + (safe_bonus) + align
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            # minimize distance; prefer align with opponent and safe positions
            score = (d * 10) - (safe_bonus) - align
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]