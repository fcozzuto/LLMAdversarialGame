def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = w // 2, h // 2
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_r = resources[0]
        best_v = -10**18
        for rx, ry in resources:
            ds = kdist(sx, sy, rx, ry)
            do = kdist(ox, oy, rx, ry)
            # Primary: race advantage. Secondary: closer. Tertiary: prefer nearer-center/escape from being corner-trapped.
            v = (do - ds) * 300 + (do - ds) * (10 if ds <= do else -2)
            v += (60 - ds) - 0.15 * (rx * rx + ry * ry) + 0.02 * (kdist(rx, ry, cx, cy))
            # Small bias to reduce opponent intercept by also preferring targets far from opponent's start direction
            v += 0.01 * (abs((ox - rx)) + abs((oy - ry)))
            if v > best_v:
                best_v = v
                best_r = (rx, ry)
        tx, ty = best_r

        best_m = (0, 0)
        best_mv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ns = kdist(nx, ny, tx, ty)
            ns2 = kdist(nx, ny, cx, cy)
            # Evaluate effect on racing: if we are leading, don't let opponent close gap too much by worsening our distance.
            nDo = kdist(ox, oy, tx, ty)
            lead_term = (nDo - ns) * 300
            # Additionally, slightly minimize our distance to target; and keep moving generally toward the target
            closeness = -ns * 18 - ns2 * 1.5
            block_term = 0
            if (nx, ny) in obstacles:
                block_term = -10**6
            v = lead_term + closeness + block_term
            if v > best_mv:
                best_mv = v
                best_m = (dx, dy)
        return [int(best_m[0]), int(best_m[1])]

    # If no resources known, drift toward center and avoid obstacles.
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = -kdist(nx, ny, cx, cy) * 5
        # Prefer keeping distance from opponent to reduce risk
        v += kdist(nx, ny, ox, oy) * 0.1
        if v > best_v:
            best_v = v
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]