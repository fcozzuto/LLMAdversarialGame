def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        # Deterministic fallback: head away from opponent toward center-ish
        tx = w // 2
        ty = h // 2
        best = (0, 0)
        best_sc = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sc = man(nx, ny, tx, ty) - man(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]]

    # Heuristic: pick next move that maximizes margin over opponent on resources,
    # while strongly minimizing our distance to the best resource.
    best = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_local = -10**18
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent, then shortest our distance.
            sc = (d_opp - d_self) * 1000 - d_self
            # Small deterministic bias toward moving generally toward resource set.
            sc -= (rx - nx) * 0.0001 + (ry - ny) * 0.0001
            if sc > best_local:
                best_local = sc
        # Prefer overall moves with higher best_local.
        if best_local > best_sc:
            best_sc = best_local
            best = (dx, dy)

    return [best[0], best[1]]