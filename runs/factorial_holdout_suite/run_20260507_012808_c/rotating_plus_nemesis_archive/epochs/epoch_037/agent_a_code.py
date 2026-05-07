def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))

    if not targets:
        return [0, 0]

    best_t = targets[0]
    best_d = cheb(sx, sy, best_t[0], best_t[1])
    for t in targets[1:]:
        d = cheb(sx, sy, t[0], t[1])
        if d < best_d:
            best_d = d
            best_t = t

    tx, ty = best_t
    candidates = [(-1, -1), (0, -1), (1, -1),
                  (-1, 0),  (0, 0), (1, 0),
                  (-1, 1),  (0, 1), (1, 1)]

    best_move = (0, 0)
    best_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        hit = (nx, ny) in obs
        dist = cheb(nx, ny, tx, ty)
        # Tie-break deterministically: fewer turns direction preference (toward target), then dx, then dy
        move_tow = abs((tx - nx)) - abs((tx - sx))  # negative means closer in x-abs
        move_toy = abs((ty - ny)) - abs((ty - sy))
        key = (1 if hit else 0, dist, move_tow, move_toy, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]