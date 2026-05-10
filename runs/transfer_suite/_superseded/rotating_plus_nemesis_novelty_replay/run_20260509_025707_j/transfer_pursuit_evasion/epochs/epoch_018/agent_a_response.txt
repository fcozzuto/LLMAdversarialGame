def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position", None)
    op = observation.get("opponent_position", None)
    if w <= 0 or h <= 0 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)):
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = role == "evader"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x, y, a, b):
        dx = abs(x - a); dy = abs(y - b)
        return dx if dx > dy else dy

    def min_obs_dist(x, y):
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

    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist = cheb(nx, ny, ox, oy)
        od = min_obs_dist(nx, ny)

        # pursuer: minimize distance, lightly avoid obstacles; evader: maximize distance, avoid getting too close to obstacles
        score = dist - 0.25 * od if not is_evader else (-dist + 0.15 * od)

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move