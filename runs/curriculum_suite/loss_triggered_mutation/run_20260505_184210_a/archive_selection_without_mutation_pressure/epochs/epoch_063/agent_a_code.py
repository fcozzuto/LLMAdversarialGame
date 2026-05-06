def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Estimate which resource opponent is likely to chase: nearest to opponent.
    opp_target = min(resources, key=lambda r: md(ox, oy, r[0], r[1]))
    tx, ty = opp_target

    # Additional bias: sweep_rows tends to progress by rows; favor aligning with opponent's row.
    row_bias = 0 if ox == sy else 1

    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_to_target = md(nx, ny, tx, ty)
        opp_to_target = md(ox, oy, tx, ty)

        # If we can beat their distance to target, prioritize strong interception.
        intercept = (my_to_target - opp_to_target)

        # Resource spread: also consider moving toward some resource, but primarily the opponent target.
        # Penalize being far from all resources.
        nearest_any = min(md(nx, ny, rx, ry) for rx, ry in resources)

        # Stay safe from obstacles indirectly: mild penalty for moves that keep us adjacent to blocked cells.
        adj_block = 0
        for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)):
            if (ax, ay) in obstacles:
                adj_block += 1

        val = 1000 * intercept + 3 * nearest_any + 25 * adj_block + 2 * row_bias * (abs(ny - oy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]