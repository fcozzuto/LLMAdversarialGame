def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

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

    # evaluate all legal adjacent moves (engine will reject invalid; we pre-filter obstacles)
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    # deterministic perturbation order so ties don't repeat across epochs
    if observation.get("turn_index", 0) % 2 == 1:
        moves = [(dx, dy) for (dx, dy) in moves if dx == 0 and dy == 0] + [m for m in moves if m != (0, 0)]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Choose best immediate target from this next position
        best_for_next = None
        for cx, cy in resources:
            self_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # maximize denial: opponent far while we are close; if impossible, just minimize our distance
            key = (opp_d - self_d, -self_d, -cx, -cy)
            if best_for_next is None or key > best_for_next[0]:
                best_for_next = (key, (cx, cy))

        # secondary objective: stay on trajectories that also reduce opponent's "next" advantage
        # (approximated using opponent->our-next vs opponent->current)
        adv = cheb(ox, oy, sx, sy) - cheb(ox, oy, nx, ny)
        key2 = (best_for_next[0][0], best_for_next[0][1], adv, -(abs(nx - w // 2) + abs(ny - h // 2)), -dx, -dy)
        if best_key is None or key2 > best_key:
            best_key = key2
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]