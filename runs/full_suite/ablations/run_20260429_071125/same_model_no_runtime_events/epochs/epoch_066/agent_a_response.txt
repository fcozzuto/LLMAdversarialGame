def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target: best relative advantage over opponent, tie-break by deterministic coords
    best_t = None
    best_key = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        advantage = do - ds  # positive means we are closer
        key = (-(advantage), ds + do, tx, ty)  # minimize negative advantage => maximize advantage
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)
    tx, ty = best_t

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Move: maximize progress to target; penalize getting closer to opponent
    cur_d = cheb(sx, sy, tx, ty)
    cur_do = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        nd_op = cheb(nx, ny, ox, oy)
        progress = cur_d - nd  # positive is good
        opp_change = nd_op - cur_do  # positive means farther from opponent
        # Obstacle-aware tie breaker by deterministic coords
        val = (progress, opp_change, -(abs(nx - tx) + abs(ny - ty)), -abs(nx - ox) - abs(ny - oy), nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]