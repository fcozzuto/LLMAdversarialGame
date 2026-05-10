def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        best_adv = None
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds
            if best_adv is None or adv > best_adv:
                best_adv = adv
        if best_adv is None:
            continue
        score = best_adv
        tie = (dx, dy)
        if best is None or score > best[0] or (score == best[0] and tie < best[1]):
            best = (score, tie, dx, dy)
    if best is None:
        return [0, 0]
    return [best[2], best[3]]