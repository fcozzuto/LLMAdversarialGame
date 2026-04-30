def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

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

    if not resources:
        for dx, dy in [(0, 0), (1, 1), (1, 0), (0, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if passable(nx, ny):
                return [dx, dy]
        return [0, 0]

    candidates = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # bigger => we are closer than opponent
        candidates.append((adv, rx, ry))
    candidates.sort(reverse=True)
    top = candidates[:4] if len(candidates) > 4 else candidates

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue

        # Prefer moves that increase relative closeness to contested targets,
        # while also reducing proximity to obstacles to avoid getting stuck.
        score = 0
        for adv, rx, ry in top:
            ds2 = cheb(nx, ny, rx, ry)
            do2 = cheb(ox, oy, rx, ry)
            score += (do2 - ds2)  # relative advantage for this target
        # Obstacle penalty: if we are adjacent to obstacles, reduce score
        if obstacles:
            near = 0
            for ax, ay in obstacles:
                if cheb(nx, ny, ax, ay) <= 1:
                    near += 1
            score -= 2 * near

        # If tie, prefer staying closer to the best target we selected
        if top:
            _, rx0, ry0 = top[0]
            score -= 0.001 * cheb(nx, ny, rx0, ry0)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if not passable(sx, sy):
        return [0, 0]
    return [best_move[0], best_move[1]]