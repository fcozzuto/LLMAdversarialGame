def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    best_move = (0, 0)
    best_key = None

    # Tie-break: maximize (opp_dist - self_dist), then smaller self_dist, then prefer moves that reduce distance to nearest resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        # Evaluate: best advantage among all resources after this move
        best_adv = None
        best_self = None
        for rx, ry in resources:
            sd = dist_cheb(nx, ny, rx, ry)
            od = dist_cheb(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_self is None or sd < best_self)):
                best_adv, best_self = adv, sd
        nearest_sd = min(dist_cheb(nx, ny, rx, ry) for rx, ry in resources)
        key = (best_adv, -best_self if best_self is not None else 0, -nearest_sd)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]