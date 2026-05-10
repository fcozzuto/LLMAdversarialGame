def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

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

    valid = []
    for p in resources:
        x, y = p[0], p[1]
        if inb(x, y) and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # Prefer resources we can reach earlier; then closer to us; then smaller coords
        key = (0 if adv > 0 else 1, -adv, sd, od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Prefer decreasing distance to target; if ties, keep move that improves our lead over opponent
        lead_improve = (d_opp - d_self)
        key = (-lead_improve, d_self, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_m is None or key < best_m[0]:
            best_m = (key, (dx, dy))

    if best_m is None:
        return [0, 0]
    return [int(best_m[1][0]), int(best_m[1][1])]