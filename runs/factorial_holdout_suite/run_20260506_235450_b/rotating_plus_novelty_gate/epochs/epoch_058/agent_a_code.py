def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_score = -10**18
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if blocked(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)

        # Relative advantage: favor collecting sooner; penalize resources where opponent is much closer.
        adv = do - ds  # positive if we are closer
        score = adv * 18 - ds * 2
        if do < ds:
            score -= (ds - do) * 6
        # Small bias toward staying away from near-by opponent when chasing contested resources
        if do <= 2 and ds <= 3:
            score -= 6

        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = [0, 0]
    best_m_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)

        # Prefer moves that reduce our distance to target.
        score = -ns * 5
        # Tie-break: prefer moves that also make target relatively less favorable to opponent (increase do - ds).
        score += (do - ns) * 3

        # Minor tie-break: keep closer to target diagonal alignment (deterministic)
        score += -abs((nx - tx) - (ny - ty))

        if score > best_m_score:
            best_m_score = score
            best_m = [dx, dy]

    return best_m