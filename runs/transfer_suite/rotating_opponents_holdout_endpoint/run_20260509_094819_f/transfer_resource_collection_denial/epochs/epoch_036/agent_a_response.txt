def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Choose target: maximize win margin (opponent distance - our distance), then closer.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = man(rx, ry, sx, sy)
        do = man(rx, ry, ox, oy)
        key = (-(do - ds), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # Secondary: if we can contest a nearby resource from opponent, slightly prefer moving that way.
    opp_targets = []
    for rx, ry in resources:
        if man(rx, ry, ox, oy) <= man(tx, ty, ox, oy):
            opp_targets.append((rx, ry))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_to_target = man(nx, ny, tx, ty)
        score = -d_to_target
        # If we step onto a resource, huge reward.
        if (nx, ny) in resources:
            score += 10**6
        # Avoid moving away from any contested resource.
        min_opp_ds = 10**9
        for rx, ry in opp_targets[:6]:
            min_opp_ds = min(min_opp_ds, man(nx, ny, rx, ry))
        score += -0.25 * min_opp_ds
        # Encourage finishing race: prefer moves that reduce our distance more than opponent's would (estimate).
        ds_now = man(sx, sy, tx, ty)
        ds_next = d_to_target
        do_now = man(ox, oy, tx, ty)
        do_next_est = do_now  # we don't know opponent move; keep light
        score += 0.1 * (ds_now - ds_next) - 0.01 * do_next_est
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]