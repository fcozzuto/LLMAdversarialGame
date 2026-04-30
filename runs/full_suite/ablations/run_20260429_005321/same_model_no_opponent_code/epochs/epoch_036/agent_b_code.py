def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    x, y = int(x), int(y)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if (x, y) in set(resources):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    opp_dist = cheb(x, y, ox, oy)
    nbr_obs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    def obstacle_pressure(nx, ny):
        s = 0
        for dx, dy in nbr_obs:
            if (nx + dx, ny + dy) in obstacles:
                s += 1
        return s

    best_target = None
    best_score = -10**9
    for rx, ry in resources:
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner, and slightly prefer closer-to-us tiles.
        score = (do - ds) * 2 - ds
        # If opponent is very close, strongly prioritize catching something first.
        if opp_dist <= 2:
            score += (do - ds) * 3
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    if best_target is None:
        # Fallback: move toward center while keeping distance from opponent.
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_target

    # Choose move that reduces distance to target; if tied, avoid obstacles and increase distance from opponent.
    best_move = (0, 0)
    best_eval = -10**9
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # Avoid corners near obstacles a bit; discourage stepping adjacent when possible.
        obs_pen = obstacle_pressure(nx, ny)
        evalv = -d_t * 5 + d_o * 2 - obs_pen * 2
        # If target is current location, take it.
        if (nx, ny) == (tx, ty):
            evalv += 1000
        if evalv > best_eval:
            best_eval = evalv
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]