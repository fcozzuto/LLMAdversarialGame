def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "evasion"))
    is_pursuer = any(k in role for k in ("pursuer", "chaser", "catcher"))
    if not (is_evader or is_pursuer):
        is_evader = False  # default to pursuer

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort()

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx if dx >= 0 else -dx if dy == 0 else max(dx if dx >= 0 else -dx, dy if dy >= 0 else -dy)

    def dist(x, y):
        return max(abs(x - ox), abs(y - oy))

    best = None
    best_score = -10**9 if is_evader else 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist(nx, ny)
        if is_evader:
            score = d * 10 - (1 if (nx, ny) in obstacles else 0)
            if (nx, ny) == (ox, oy):
                score -= 1000
            if score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            score = d * -10
            if d == 0:
                score += 10000  # strongly prefer capture
            if score < best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]