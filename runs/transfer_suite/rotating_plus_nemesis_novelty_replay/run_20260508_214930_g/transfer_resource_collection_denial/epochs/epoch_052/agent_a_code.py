def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for tx, ty in resources:
        self_t = cheb(sx, sy, tx, ty)
        opp_t = cheb(ox, oy, tx, ty)
        margin = self_t - opp_t  # negative means we arrive sooner
        # Win-possible: pick most negative margin, then smallest self_t.
        # Otherwise: minimize how far behind we are, then smallest self_t.
        key = (0, self_t, tx, ty) if margin < 0 else (1, margin, self_t, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_d = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, tx, ty)
        # Prefer smaller distance, then move that doesn't increase distance for opponent race.
        opp_dist = cheb(nx, ny, ox, oy)
        score = (dist, opp_dist, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_d = [dx, dy]

    return best_d if best_d is not None else [0, 0]