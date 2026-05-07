def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Antagonistic targeting: go for cells opponent is likely to grab soon (small opp distance),
    # but that are relatively farther from us; break ties to prioritize closer to us.
    best = None
    best_key = None
    for rx, ry in resources:
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Want: opp_d small, self_d not too small (so we "race" the opponent rather than follow her path).
        key = (-(opp_d * 1000) + (self_d * 5), -self_d, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose a move that reduces distance to target, while not stepping into obstacles.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                moves.append((d, abs(dx), abs(dy), dx, dy))
    if not moves:
        return [0, 0]

    # Deterministic: smallest distance, then prefer diagonal (smaller movement components), then lexicographic.
    moves.sort(key=lambda t: (t[0], t[1] + t[2], -max(t[1], t[2]), t[3], t[4]))
    dx, dy = moves[0][3], moves[0][4]
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]