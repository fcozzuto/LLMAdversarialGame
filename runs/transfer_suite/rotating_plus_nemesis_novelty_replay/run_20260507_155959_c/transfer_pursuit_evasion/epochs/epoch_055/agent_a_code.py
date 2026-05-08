def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or (self_role == "pursuer")

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves.sort(key=lambda t: (t[0], t[1]))  # deterministic

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_move_for(nx, ny, ex, ey):
        # One-ply evaluation for pursuer/evader: pursuer wants smaller dist, evader wants larger
        if is_pursuer:
            return -dist(nx, ny, ex, ey)
        return dist(nx, ny, ex, ey)

    best = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Small lookahead: assume opponent responds with best move (role-specific)
        opp_moves = []
        for odx, ody in moves:
            tx, ty = ox + odx, oy + ody
            if valid(tx, ty):
                opp_moves.append((tx, ty))
        if not opp_moves:
            opp_best_val = best_move_for(nx, ny, ox, oy)
        else:
            if is_pursuer:
                # Evader maximizes distance
                opp_best_val = None
                for tx, ty in opp_moves:
                    v = best_move_for(nx, ny, tx, ty)
                    if opp_best_val is None or v > opp_best_val:
                        opp_best_val = v
            else:
                # Pursuer minimizes distance
                opp_best_val = None
                for tx, ty in opp_moves:
                    v = best_move_for(nx, ny, tx, ty)
                    if opp_best_val is None or v < opp_best_val:
                        opp_best_val = v

        # Tie-breaks: avoid getting stuck; slight wall/obstacle awareness
        edge_pen = (min(nx, w - 1 - nx) + min(ny, h - 1 - ny)) * 0.001
        # Prefer staying in mobility-adjacent area: count valid neighboring cells
        mobility = 0
        for mx, my in moves:
            tx, ty = nx + mx, ny + my
            if valid(tx, ty):
                mobility += 1
        mob = mobility * (0.01 if is_pursuer else 0.02)

        # Main objective
        main = (opp_best_val if opp_best_val is not None else best_move_for(nx, ny, ox, oy))
        val = main + (edge_pen + mob if not is_pursuer else 0.5 * (edge_pen + mob))

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]