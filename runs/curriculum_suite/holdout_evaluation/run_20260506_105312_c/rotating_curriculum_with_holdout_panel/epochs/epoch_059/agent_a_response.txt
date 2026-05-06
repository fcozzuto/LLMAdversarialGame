def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = (w // 2, h // 2)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, tx, ty)
            key = (d, -dist(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Race heuristic: prefer resources where we can arrive no later than opponent.
    # Use a bias toward nearer wins, and a secondary bias toward blocking (larger opponent distance).
    def best_resource_score(px, py):
        best_key = None
        for rx, ry in resources:
            ds = dist(px, py, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Lower is better:
            # - primary: (ds - do) (negative => we can win race)
            # - secondary: ds (reach quickly)
            # - tertiary: -do (make opponent farther)
            key = (ds - do, ds, -do, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
        return best_key

    cur_key = best_resource_score(sx, sy)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        key = best_resource_score(nx, ny)
        # Prefer improving race potential; if equal, prefer smaller move cost to stick to strong path.
        move_cost = dist(nx, ny, sx, sy)
        final_key = (key, move_cost, dx, dy)
        if best is None or final_key < best[0]:
            best = (final_key, dx, dy)

    if best:
        return [best[1], best[2]]
    return [0, 0]