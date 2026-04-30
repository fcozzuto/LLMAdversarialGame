def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    me = tuple(observation["self_position"])
    opp = tuple(observation["opponent_position"])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(o) for o in observation.get("obstacles", []) or [])
    obs = obstacles

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = me[0] + dx, me[1] + dy
        if inb(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Choose best resource: maximize advantage (opp farther - me closer), break ties by closer to center then farther from opp.
    center = (w // 2, h // 2)
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obs:
            continue
        dm = cheb(me, (rx, ry))
        do = cheb(opp, (rx, ry))
        adv = do - dm
        # Prefer decisive advantage; then prefer small dm; then center proximity; then keep away from opp.
        key = (adv, -dm, -(cheb((rx, ry), center)), do, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        best_r = center

    tx, ty = best_r
    # Move to reduce distance to target while also not allowing opponent to improve too much.
    best_move = (0, 0)
    best_val = None
    for dx, dy in legal:
        nx, ny = me[0] + dx, me[1] + dy
        dm2 = cheb((nx, ny), (tx, ty))
        do = cheb(opp, (tx, ty))
        my_adv = do - dm2
        # Secondary: keep my distance small and stable; avoid oscillation by slight preference for moving toward center when tied.
        val = (my_adv, -dm2, -cheb((nx, ny), center), -abs(dx) - abs(dy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]