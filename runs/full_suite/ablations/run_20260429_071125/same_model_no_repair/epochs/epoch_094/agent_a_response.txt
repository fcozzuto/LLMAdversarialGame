def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda d: (abs(d[0]) + abs(d[1]) == 2, d[0], d[1]))

    # Choose target resource: prefer ones we can reach earlier; break ties by larger "lead" and then lower absolute distance sum.
    best_r = None
    best = None
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Earlier reach is primary; then maximize lead (do-du); then smaller du; then deterministic coord.
        key = (0 if du <= do else 1, -(do - du), du, rx, ry)
        if best is None or key < best:
            best = key
            best_r = (rx, ry)
    rx, ry = best_r

    # If opponent is closer or equal, switch to a blocking/contesting move: head to a resource where we are not worse, else toward nearest.
    du_t = cheb(sx, sy, rx, ry)
    do_t = cheb(ox, oy, rx, ry)
    target = (rx, ry)
    if du_t > do_t:
        cand = None
        best2 = None
        for r in resources:
            rrx, rry = r
            du = cheb(sx, sy, rrx, rry)
            do = cheb(ox, oy, rrx, rry)
            if du <= do:
                key2 = (du, rrx, rry, (do - du))
                if best2 is None or key2 < best2:
                    best2 = key2
                    cand = (rrx, rry)
        if cand is not None:
            target = cand
        else:
            # fall back to our nearest resource
            target = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    tx, ty = target

    # Evaluate each candidate step with local heuristic: reduce our distance to target, and keep away from squares that let opponent get closer to same target.
    # Also lightly avoid paths that move closer to obstacles (local safety).
    obstacle_list = obstacles

    def safe_score(x, y):
        # fewer adjacent obstacles is better
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacle_list:
                    cnt += 1
        return -cnt

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not move_ok(nx, ny):
            nx, ny = sx, sy
        my_d = cheb(nx, ny, tx, ty)
        my_now = cheb(sx, sy, tx, ty)

        opp_d_before = cheb(ox, oy, tx, ty)
        # Predict opponent likely move: try to reduce their distance to our target; choose the best among valid moves deterministically.
        opp_best_d = None
        for odx, ody in moves:
            onx, ony = ox + od