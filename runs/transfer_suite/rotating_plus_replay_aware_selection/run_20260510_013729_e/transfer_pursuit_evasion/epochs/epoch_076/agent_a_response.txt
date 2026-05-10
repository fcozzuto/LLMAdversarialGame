def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role)

    chasing = (not self_ev) or opp_ev  # if we're pursuer, chase; if we're evader, run

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    def clamp(nx, ny):
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        return nx, ny

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        ddx = abs(nx - ox)
        ddy = abs(ny - oy)
        cheb = ddx if ddx > ddy else ddy
        # Additional mild tie-break: prefer moving toward/away in x then y
        tie = (ddx, ddy) if not chasing else (-ddx, -ddy)
        val = (-cheb, tie) if chasing else (cheb, tie)
        if best is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        # All candidate moves blocked; allow obstacles but still choose deterministically
        for dx, dy in moves:
            nx, ny = clamp(sx + dx, sy + dy)
            ddx = abs(nx - ox)
            ddy = abs(ny - oy)
            cheb = ddx if ddx > ddy else ddy
            tie = (ddx, ddy) if not chasing else (-ddx, -ddy)
            val = (-cheb, tie) if chasing else (cheb, tie)
            if best is None or val < best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]