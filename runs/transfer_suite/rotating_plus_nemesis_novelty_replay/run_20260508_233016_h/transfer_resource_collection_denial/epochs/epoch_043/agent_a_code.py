def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_target(px, py):
        best = None
        for rx, ry in resources:
            myd = man(px, py, rx, ry)
            opd = man(ox, oy, rx, ry)
            win = 1 if myd <= opd else 0
            # Prefer winning (win=1). If not, prefer contesting where opponent is very close.
            # tie-breaker: smaller myd (faster pickup), then lexicographic by position.
            key = (0 if win else 1, myd, -opd if win else -opd, rx, ry) if win else (1, -(opd - myd), myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry), myd, opd)
        return best[1], best[2], best[3]

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        (tx, ty), myd, opd = best_target(nx, ny)
        # Evaluate how well this move sets us up relative to opponent for the chosen target.
        # Higher is better; keep deterministic.
        score = (0 if myd <= opd else 1, myd - opd, myd, -opd, tx, ty, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move in ([-1, -1], [0, -1], [1, -1], [-1, 0], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]) else [0, 0]