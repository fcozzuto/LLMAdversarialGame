def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    # If resources exist, pick the move that maximizes advantage for the best reachable resource.
    best_move = [0, 0]
    best_val = None
    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if not legal(nx, ny):
            continue
        if resources:
            best_res_val = None
            best_res = None
            for rx, ry in resources:
                md = dist2(nx, ny, rx, ry)
                od = dist2(ox, oy, rx, ry)
                # Favor being closer than opponent; break ties by closeness to us and slightly away from opponent.
                val = (od - md) * 100000 - md * 3 + (dist2(nx, ny, ox, oy) * 0.001)
                if best_res_val is None or val > best_res_val:
                    best_res_val = val
                    best_res = (rx, ry)
            # Prefer moves that also reduce our direct distance to the chosen resource.
            rx, ry = best_res
            base = best_res_val
            # Encourage stepping along the direction to the chosen resource by penalizing distance to it.
            md_now = dist2(nx, ny, rx, ry)
            val = base - md_now * 2
        else:
            # No visible resources: head to the most “useful” corner (closest to us, farthest from opponent).
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            best_corner = None
            best_corner_val = None
            for cx, cy in corners:
                d1 = dist2(nx, ny, cx, cy)
                d2 = dist2(ox, oy, cx, cy)
                v = d2 * 0.0001 - d1
                if best_corner_val is None or v > best_corner_val:
                    best_corner_val, best_corner = v, (cx, cy)
            ccx, ccy = best_corner
            val = -dist2(nx, ny, ccx, ccy) + dist2(nx, ny, ox, oy) * 0.0001
        if best_val is None or val > best_val:
            best_val = val
            best_move = [mx, my]

    return [int(best_move[0]), int(best_move[1])]