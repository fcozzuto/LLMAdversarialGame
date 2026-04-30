def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (x + dx, y + dy) in obst:
                    r += 3
        return r

    def choose_resource_for_state(x, y):
        if not resources:
            return None, 0
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # want to be closer than opponent; also prefer nearby resources
            key = (do - ds, -ds, -rx, -ry)  # maximize (do-ds), then minimize ds
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best, best_key[0] if best_key is not None else 0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        target, adv = choose_resource_for_state(nx, ny)
        # If we step onto a resource, strongly prefer it.
        pickup = 2000 if (nx, ny) in {(r[0], r[1]) for r in resources} else 0
        # Block/contest: if we can reach a target sooner than opponent, bias it.
        contest = 0
        if target is not None:
            ds = cheb(nx, ny, target[0], target[1])
            do = cheb(ox, oy, target[0], target[1])
            if ds < do:
                contest = 800 // (1 + ds)
            elif ds == do:
                contest = 120
        # Prefer moves that reduce distance to the chosen target directly (when contesting).
        direct = 0
        if target is not None:
            direct = -cheb(nx, ny, target[0], target[1])
        score = pickup + 50 * adv + contest + 5 * direct - risk(nx, ny)
        # Small tie-break: deterministic preference toward increasing x then y
        if score > best_score or (score == best_score and (dx, dy) > best_move):
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]