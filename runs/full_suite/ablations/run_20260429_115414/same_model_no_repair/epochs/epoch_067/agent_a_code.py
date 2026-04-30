def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_resource_dist(px, py):
        if not resources:
            return cheb(px, py, w // 2, h // 2)
        best = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < best:
                best = d
        return best

    # If no resources, head to center while avoiding obstacles.
    if not resources:
        cx, cy = w // 2, h // 2
        bx, by = sx, sy
        best = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not passable(nx, ny):
                continue
            sc = -cheb(nx, ny, cx, cy)
            if sc > best:
                best = sc
                bx, by = nx, ny
        return [bx - sx, by - sy]

    opp_base = best_resource_dist(ox, oy)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        our_d = best_resource_dist(nx, ny)
        # Deny by increasing opponent's advantage; also avoid getting too close to nearest.
        score = (opp_base - our_d) * 1000 - our_d

        # Tiny tie-break: prefer moves that reduce distance to any resource uniquely.
        tie = 0
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) == our_d:
                tie = cheb(ox, oy, rx, ry) - our_d
                break
        score += tie

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]