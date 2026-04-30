def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def in_bounds(px, py):
        return 0 <= px < w and 0 <= py < h

    occ = set()
    for p in obstacles:
        if p and len(p) >= 2:
            occ.add((int(p[0]), int(p[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    valid = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and (nx, ny) not in occ:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def score_target(rx, ry):
        d_self = cheb(x, y, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; then maximize margin; else minimize our distance
        # Tie-break deterministically by coordinates.
        return (d_opp <= d_self, -(d_opp - d_self), d_self, rx, ry)

    best = None
    best_rx, best_ry = None, None
    for p in resources:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if in_bounds(rx, ry):
                k = score_target(rx, ry)
                if best is None or k < best:
                    best = k
                    best_rx, best_ry = rx, ry

    # If no resources, move to reduce distance to opponent's nearest resource if any, else stay.
    if best_rx is None:
        return [0, 0]

    # Greedy step: among valid moves, minimize distance to chosen target; break ties toward staying still.
    best_move = None
    best_k = None
    for dx, dy, nx, ny in valid:
        d_self = cheb(nx, ny, best_rx, best_ry)
        d_opp_to = cheb(ox, oy, best_rx, best_ry)
        # slight preference to moves that don't let opponent become much closer (via reducing our slack)
        slack = d_opp_to - cheb(nx, ny, best_rx, best_ry)
        k = (d_self, -slack, dx == 0 and dy == 0, dx, dy)
        if best_k is None or k < best_k:
            best_k = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]