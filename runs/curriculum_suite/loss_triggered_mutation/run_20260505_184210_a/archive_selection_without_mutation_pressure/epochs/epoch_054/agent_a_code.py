def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # If no resources, drift to reduce opponent lead by moving away from direct approach line.
    if not resources:
        best = None
        best_val = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # Favor increasing distance to opponent slightly while staying centered.
            val = (md(nx, ny, ox, oy)) - 0.01 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    best = None
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_near = 10**9
        best_adv = -10**9  # want op_dist - my_dist large (we get there sooner)
        for rx, ry in resources:
            d_my = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            if d_my < my_near:
                my_near = d_my
            adv = d_op - d_my
            if adv > best_adv:
                best_adv = adv
        # Encourage immediate capture potential and counter-advantage.
        val = best_adv * 10 - my_near
        # Small tie-break: prefer moving that also increases distance from opponent (avoid being contested).
        val += 0.02 * md(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]