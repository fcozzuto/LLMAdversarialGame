def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]

    # Opportunistic race: prefer moves that make us reach some resource earlier than opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh: 
            continue
        if (nx, ny) in obstacles:
            continue

        move_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Primary: maximize odds opponent slower; Secondary: smaller our distance.
            v = (od - sd) * 1000 - sd
            # Small bias toward collecting nearer resources in general (reduces dithering).
            v -= cheb(nx, ny, sx, sy)
            if v > move_best:
                move_best = v

        # Tie-break: prefer moves that directly land on a resource.
        on_res = 1 if (nx, ny) in [tuple(r) for r in resources] else 0
        score = move_best + on_res * 10**6
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If everything is blocked, stay.
    if best_score == -10**18:
        return [0, 0]
    return [best_move[0], best_move[1]]