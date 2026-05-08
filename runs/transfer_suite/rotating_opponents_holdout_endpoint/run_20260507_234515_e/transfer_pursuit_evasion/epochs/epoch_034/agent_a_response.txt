def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or (("direct" in role) and ("evad" not in role)) or (role == "")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def far_corner_score(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # maximize distance from opponent by going toward farthest corner from opponent
        best = -10**9
        for cx, cy in corners:
            d = abs(cx - ox) + abs(cy - oy)
            # prefer corners that also keep us moving there
            step = abs(cx - x) + abs(cy - y)
            val = d * 100 - step
            if val > best:
                best = val
        return best

    best_dxdy = (0, 0)
    best_sc = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            sc = -10**12 if pursuer else -10**12
        else:
            dist = abs(nx - ox) + abs(ny - oy)
            # tie-breakers discourage staying still for evader and staying for pursuer
            stay_pen = 1 if (nx == sx and ny == sy) else 0
            # small deterministic bias toward moving diagonally first to avoid wall-run traps
            diag_bias = 1 if (dx != 0 and dy != 0) else 0
            if pursuer:
                # minimize distance; avoid staying; prefer moves that continue to reduce distance
                sc = -dist * 1000 + diag_bias * 3 - stay_pen * 5
            else:
                # maximize distance; prefer far corner direction; avoid staying
                sc = dist * 1000 + diag_bias * 3 + far_corner_score(nx, ny) * 0.01 - stay_pen * 5

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]