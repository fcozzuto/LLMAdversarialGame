def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_value(px, py):
        # Prefer securing a resource earlier; if none, move to worsen opponent's prospects near their closest resource.
        best = -10**9
        for tx, ty in resources:
            ds = cheb(px, py, tx, ty)
            do = cheb(ox, oy, tx, ty)
            margin = do - ds
            base = margin * 100 - ds
            # Extra tie-break: resources closer to opponent get higher denial when margin is negative.
            if margin < 0:
                base = base + (300 - do * 10) - ds
            # Slight focus on mid-game: reduce long detours.
            base = base - 2 * (ds > 6)
            if base > best:
                best = base
        return best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                candidates.append((dx, dy, best_value(nx, ny)))
            else:
                # Engine would keep still if invalid; emulate as (0,0) option.
                candidates.append((0, 0, best_value(sx, sy)))

    # Deterministic: choose max value; then lexicographic preference (dx, dy).
    best = (-10**18, 0, 0)
    for dx, dy, val in candidates:
        key = (val, -abs(dx) - abs(dy), -dx, -dy)
        if key > (best[0], -abs(best[1]) - abs(best[2]), -best[1], -best[2]):
            best = (val, dx, dy)
    return [int(best[1]), int(best[2])]