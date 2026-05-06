def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def manh(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0: d1 = -d1
        d2 = y1 - y2
        if d2 < 0: d2 = -d2
        return d1 + d2

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # If no resources visible, drift toward opponent but keep away slightly (to avoid collisions / block).
    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = manh(nx, ny, ox, oy) * 0.7 - manh(nx, ny, 0, 0) * 0.0001
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    # Score moves by: closeness to nearest resource, and distancing from opponent.
    # Also add a deterministic preference: favor reducing distance in y first, then x (helps consistency).
    best_val = None
    best_move = (0, 0)
    # deterministic ordering tie-break
    ordered = sorted(legal, key=lambda t: (t[1], t[0]))
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        min_res = None
        for rx, ry in resources:
            d = manh(nx, ny, rx, ry)
            if min_res is None or d < min_res:
                min_res = d
        opp_dist = manh(nx, ny, ox, oy)
        # Weight opponent distance more when resources remain plentiful (avoid trading too early).
        rem = observation.get("remaining_resource_count")
        if rem is None:
            rem = len(resources)
        opp_w = 0.25 if rem > 3 else 0.15
        # Tie-break by "progress": prefer smaller y distance then x distance to the nearest resource
        # (approx: use current nearest resource to define direction).
        near = min(resources, key=lambda p: manh(nx, ny, p[0], p[1]))
        ty, tx = near[1], near[0]
        prog_y = abs(sy - ty) - abs(ny - ty)
        prog_x = abs(sx - tx) - abs(nx - tx)
        val = min_res + opp_w * (-opp_dist) - 0.02 * prog_y - 0.01 * prog_x
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]