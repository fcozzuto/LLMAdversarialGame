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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose target that maximizes (opp_dist - our_dist); tie-break by smallest our_dist then coords.
    best_target = None
    best_tkey = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        key = (-(d2 - d1), d1, rx, ry)  # minimize negative advantage => maximize advantage
        if best_tkey is None or key < best_tkey:
            best_tkey = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Evaluate one-step move by future advantage against chosen target, plus tie-break on resource-coverage.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Primary: maximize immediate advantage (opp_d - our_d)
        adv = opp_d - our_d

        # Secondary: if opponent is closer to this target, try to "deny" by reducing opp reach quickly.
        deny = 0
        if opp_d < our_d:
            deny = (our_d - opp_d)

        # Tertiary: consider how well we align to other resources (avoid getting trapped far from all).
        # Deterministic small lookahead score (no full search).
        close_cnt = 0
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            if cheb(nx, ny, rx, ry) <= cheb(nx, ny, tx, ty) + 1:
                close_cnt += 1

        val = (adv, -deny, -close_cnt, cheb(nx, ny, tx, ty), nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]