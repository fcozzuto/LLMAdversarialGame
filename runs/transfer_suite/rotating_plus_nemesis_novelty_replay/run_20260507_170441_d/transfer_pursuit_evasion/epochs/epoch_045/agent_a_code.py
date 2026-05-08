def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    is_evader = ("evader" in self_role) or ("evader" in opp_role and "pursuer" not in self_role)
    if ("pursuer" in self_role) and ("evader" in opp_role):
        is_evader = False

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        cx = abs(ox - nx)
        cy = abs(oy - ny)
        cheb = cx if cx >= cy else cy
        man = cx + cy

        # obstacle "pressure": fewer available moves from next state is worse for evader, better for pursuer
        avail = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                avail += 1

        if is_evader:
            # maximize escape distance; slight preference for moves with MORE mobility
            val = (cheb, man, avail)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            # minimize escape distance; tie-break by reducing manhattan and encouraging low escape mobility
            val = (-cheb, -man, -avail)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]