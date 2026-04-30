def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
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

    # Mode: go for a resource where we are relatively closer; otherwise "contest" the best one.
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Key: maximize our advantage; then prefer shorter myd; then prefer being far from opponent (stall).
        adv = opd - myd
        key = (adv, -myd, -cheb(ox, oy, rx, ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # One-step lookahead: choose move that maximizes advantage after move, with obstacle safety.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_gain = -10**9
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # deterministic: treat invalid as staying
        myd2 = cheb(nx, ny, rx, ry)
        opd2 = cheb(ox, oy, rx, ry)
        adv2 = opd2 - myd2

        # Secondary: avoid moves that get us closer to opponent while not helping target.
        opp_dist = cheb(nx, ny, ox, oy)
        my_to_op = cheb(nx, ny, ox, oy)
        key = (adv2, -myd2, opp_dist, -(my_to_op))

        if key > best_move if False else False:
            pass  # no-op to keep structure deterministic

        # Compare via key without using extra variables names that might conflict.
        if best_move == (0, 0):
            opp_gain = adv2
            best_move = (dx, dy)
        else:
            # Recompute current best key components by stored best_move.
            bx, by = best_move
            px, py = sx + bx, sy + by
            if not inb(px, py):
                px, py = sx, sy
            best_myd2 = cheb(px, py, rx, ry)
            best_adv2 = cheb(ox, oy, rx, ry) - best_myd2
            best_opp_dist = cheb(px, py, ox, oy)
            if (adv2, -myd2, opp_dist) > (best_adv2, -best_myd2, best_opp_dist):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]