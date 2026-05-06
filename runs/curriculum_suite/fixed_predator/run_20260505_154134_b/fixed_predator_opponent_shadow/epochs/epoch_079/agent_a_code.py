def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Target: maximize advantage over opponent, but bias toward nearer resources for reliability.
    best = None
    best_key = None
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        # key: (how much we are behind; we want opponent closer => opp_d-self_d small/negative? Actually advantage = self_d-opp_d)
        adv = self_d - opp_d  # smaller is better (we reach sooner or tie)
        # Prefer resources where we can be at least as fast as opponent; then closer.
        key = (adv, self_d, -cx, -cy)
        if best_key is None or key < best_key:
            best_key = key
            best = (cx, cy)

    tx, ty = best

    # Candidate move selection with obstacle avoidance and slight tendency to reduce distance to target.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            hit = (nx, ny) in obs
            # If engine rejects, we "simulate" by penalizing moves into obstacles heavily.
            dist = cheb(nx, ny, tx, ty)
            # Also penalize moves that let opponent get closer to the same target.
            opp_dist = cheb(ox, oy, tx, ty)
            # Keep opponent-distance effect minimal; main goal is capturing.
            key = (hit, dist, -dx, -dy)
            moves.append((key, [dx, dy]))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0])
    return moves[0][1]