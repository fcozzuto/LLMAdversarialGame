def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacle_set = set((x, y) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick resource where we have the best chance to arrive earlier (tie -> closer).
    best = None
    best_margin = None
    best_ds = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # larger => we arrive not later
        if best is None or margin > best_margin or (margin == best_margin and (ds < best_ds or (ds == best_ds and (rx, ry) < best))):
            best = (rx, ry)
            best_margin = margin
            best_ds = ds
    tx, ty = best

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacle_set:
            continue

        my_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Prefer moving closer to target, and prefer increasing our arrival advantage.
        # Small tie-break: avoid steps that increase distance to the opponent's current position too much.
        val = (opp_d - my_d) * 10_000 - my_d
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]