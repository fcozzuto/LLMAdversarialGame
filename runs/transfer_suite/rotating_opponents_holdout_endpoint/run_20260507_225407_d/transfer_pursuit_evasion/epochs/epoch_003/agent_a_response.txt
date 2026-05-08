def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("catch" in role) or ("purs" in opp_role and "evad" not in role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbors_free(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if ok(nx, ny):
                    c += 1
        return c

    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            cheb = max(abs(nx - ox), abs(ny - oy))
            free = neighbors_free(nx, ny)
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)

            # obstacle "risk": how many directions are blocked from this cell
            blocked = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    tx, ty = nx + adx, ny + ady
                    if adx == 0 and ady == 0:
                        continue
                    if not ok(tx, ty):
                        blocked += 1

            # small deterministic tie-breaker: prefer moves closer to straight-line direction
            dir_pref = 0
            if (dx == 0) ^ (dy == 0):
                # discourage purely axial if diagonal would also reduce distance
                if cheb == 0:
                    dir_pref = 0
                else:
                    diag_possible = ok(sx + (1 if ox > sx else -1 if ox < sx else 0), sy + (1 if oy > sy else -1 if oy < sy else 0))
                    dir_pref = -1 if diag_possible else 0

            if is_pursuer:
                score = (-cheb * 1000) + (free * 5) - (blocked * 3) + (far_corner * 0.1) + dir_pref
            else:
                score = (cheb * 1000) + (free * 6) - (blocked * 6) + (far_corner * 2) + dir_pref

            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))

    return [best[1][0], best[1][1]] if best is not None else [0, 0]