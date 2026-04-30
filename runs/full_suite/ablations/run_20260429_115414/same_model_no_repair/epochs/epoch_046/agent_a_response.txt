def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_key = None  # maximize adv; tie-break: smaller our_d; then coords
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        adv = opp_d - our_d
        key = (-adv, our_d, rx, ry)  # smallest key => best adv (largest) then min our_d
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    if (sx, sy) == (tx, ty):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        adv = opp_d - our_d
        s_key = (-adv, our_d, nx, ny)  # maximize adv, then min our_d, then determinism
        if best_s is None or s_key < best_s:
            best_s = s_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]