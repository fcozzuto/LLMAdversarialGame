def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for it in (observation.get("obstacles") or []):
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) and ("evader" not in opp_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    turn = int(observation.get("turn_index", 0))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_dxdy = (0, 0)
    best_key = None

    # corners to bias movement deterministically
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    target_corner = corners[turn % 4]
    tx, ty = target_corner

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Distance to opponent (capture if equal for radius 0)
        dd = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Distance from chosen corner (evader tries to get away; pursuer avoids corner if needed)
        dc = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)

        # Score: evader maximizes safety; pursuer minimizes distance to evader.
        if evader:
            # Strongly avoid being on opponent tile (dd==0) then push to farthest dd; tie-break by corner distance.
            key = (-(0 if dd == 0 else 1), -dd, -dc, dx, dy)  # lowest lex preferred? invert by using negatives
            # Convert to minimization: want maximal dd, maximal dc, and not dd==0.
            # We'll instead create minimization key explicitly:
            key = (0 if dd == 0 else 1, -dd, -dc, dx, dy)
        else:
            # Pursuer: minimize dd; tie-break by prefer moving toward corner for determinism (arbitrary but consistent).
            key = (dd, -(dc), dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]