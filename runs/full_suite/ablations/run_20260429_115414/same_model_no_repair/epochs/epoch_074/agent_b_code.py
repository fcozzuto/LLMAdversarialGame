def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))

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

    def passable(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def best_resource():
        if not resources:
            return (w // 2, h // 2)
        best = None
        best_adv = -10**18
        # Deterministic tie-break: lowest (x,y) lex for equal adv.
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # higher = we are closer than opponent
            if adv > best_adv or (adv == best_adv and (rx, ry) < best):
                best_adv = adv
                best = (rx, ry)
        return best

    tx, ty = best_resource()

    # Obstacle proximity: prefer moves that increase minimum distance to obstacles.
    obs_list = list(obstacles)

    def min_obst_dist(x, y):
        if not obs_list:
            return 99
        best = 10**9
        for px, py in obs_list:
            d = cheb(x, y, px, py)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18
    # Also consider opponent distance to target after our move (steering away from resources they'll take).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        # If we are reducing our distance while keeping opponent not too close; obstacle steering.
        score = (op_d - my_d) * 5 - my_d * 1.2 + min_obst_dist(nx, ny) * 0.7
        # Mild preference for moving generally toward target to avoid dithering.
        score += -cheb(nx, ny, tx, ty) * 0.2
        # Deterministic tie-break: lex order of (dx,dy).
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]