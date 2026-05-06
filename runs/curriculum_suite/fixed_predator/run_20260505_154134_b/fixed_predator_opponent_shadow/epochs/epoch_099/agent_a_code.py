def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    if not resources:
        return [0, 0]

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((int(p[0]), int(p[1])))

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

    # Pick a target that we can reach no slower than (or faster than) opponent, preferring big advantage
    best_r = None
    best_key = None
    for cx, cy in resources:
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        # prioritize opponent farther, then closer to us, then deterministic tie-break by position
        key = (od - sd, -sd, -cx, -cy)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (cx, cy)
    tx, ty = best_r

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    candidates.append((dx, dy, nx, ny))

    # Evaluate moves by immediate distance advantage to target; also lightly avoid moving toward opponent
    best_move = None
    best_val = None
    for dx, dy, nx, ny in candidates:
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # if we can get to target sooner than opponent, strongly prefer
        adv = opp_d - self_d
        # discourage giving opponent an easier chase: increase their distance to us
        opp_to_us = cheb(ox, oy, nx, ny)
        self_to_us = cheb(sx, sy, ox, oy)
        # deterministic tie-break using dx,dy and resulting coordinates
        val = (adv, opp_to_us - self_to_us, -self_d, -nx, -ny, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]