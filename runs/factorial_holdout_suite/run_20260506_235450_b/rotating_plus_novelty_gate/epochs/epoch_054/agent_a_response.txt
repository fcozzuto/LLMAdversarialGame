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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_r = None
    best_key = None
    for r in resources:
        if not isinstance(r, (list, tuple)) or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if blocked(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner than opponent; also penalize long travel.
        key = (od - sd, -(sd), -cheb(ox, oy, sx, sy), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        # No reachable resources: drift toward the corner farther from opponent (deterministic fallback).
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (cheb(ox, oy, c[0], c[1]) - cheb(sx, sy, c[0], c[1]), c[0], c[1]))
        rx, ry = tx, ty
    else:
        rx, ry = best_r

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        sd2 = cheb(nx, ny, rx, ry)
        od2 = cheb(ox, oy, rx, ry)
        # Score move by immediate "race advantage" and reduced distance to target.
        race = (od2 - sd2)
        opp_dist = cheb(nx, ny, ox, oy)
        score = (race, -(sd2), opp_dist)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]