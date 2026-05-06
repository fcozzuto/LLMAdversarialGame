def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # If we are on a resource, wait for pickup deterministically
    for r in resources:
        if int(r[0]) == sx and int(r[1]) == sy:
            return [0, 0]

    # Target: deterministic resource we can reach earlier than opponent; else closest by our distance
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # prioritize "win the race", then smaller own distance, then stable tie-break
        key = (0 if sd < od else 1, sd - od, sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is not None:
        tx, ty = best[1]
    else:
        # No resources: drift toward center to reduce exposure
        tx, ty = w // 2, h // 2

    # Choose next step that heads toward target while avoiding obstacles
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = cheb(nx, ny, tx, ty)
        opp_dist = cheb(ox, oy, tx, ty)
        # prefer reducing our distance; penalize moves that let opponent "race" us too easily
        score = (dist, cheb(sx, sy, tx, ty) - dist, abs(nx - tx) + abs(ny - ty), abs(ox - nx) + abs(oy - ny), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # If all legal moves are blocked, stay
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]