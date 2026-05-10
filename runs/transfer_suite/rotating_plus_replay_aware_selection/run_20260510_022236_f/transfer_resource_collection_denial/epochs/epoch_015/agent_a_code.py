def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    cand = []
    for r in resources[:30]:
        try:
            x, y = r[0], r[1]
        except Exception:
            continue
        if inb(x, y) and (x, y) not in obs:
            cand.append((x, y))
    if not cand:
        cand = [(ox, oy)]

    def risk(x, y):
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            if (x + ax, y + ay) in obs:
                return 1
        return 0

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        min_self = 10**9
        min_opp = 10**9
        for tx, ty in cand:
            min_self = min(min_self, cheb(nx, ny, tx, ty))
            min_opp = min(min_opp, cheb(ox, oy, tx, ty))
        score = (min_opp - min_self) * 10 - min_self - 3 * risk(nx, ny)
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    dx, dy = best
    return [int(dx), int(dy)]