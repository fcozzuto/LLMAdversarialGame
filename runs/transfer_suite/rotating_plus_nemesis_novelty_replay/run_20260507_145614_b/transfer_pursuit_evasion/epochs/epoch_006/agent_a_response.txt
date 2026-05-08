def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursur" in role)

    obst = set()
    for p in observation.get("obstacles", []):
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    best = None
    bestv = None
    # tie-break: deterministic preference order
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if nx == ox and ny == oy:
            return [dx, dy]

        # opponent response: 1-step minimax on next distance
        opp_best = None
        opp_val = None
        for odx, ody in deltas:
            mx, my = ox + odx, oy + ody
            if not legal(mx, my):
                continue
            # capture for pursuer check (if opponent moves onto us, they might be pursuer/capture only ends game)
            if mx == nx and my == ny:
                d = 0
            else:
                d = dist2(nx, ny, mx, my)
            if opp_best is None:
                opp_best = (mx, my)
                opp_val = d
            else:
                if pursuer:
                    # opponent is evader: maximize distance
                    if d > opp_val:
                        opp_val = d
                        opp_best = (mx, my)
                else:
                    # opponent is pursuer: minimize distance
                    if d < opp_val:
                        opp_val = d
                        opp_best = (mx, my)

        # score with slight obstacle/edge stability bias: prefer staying closer to board center when tied
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 1e-6

        if pursuer:
            val = -opp_val + center_bias  # maximize negative distance -> minimize distance worst-case
            better = (best is None) or (val > bestv)
        else:
            val = opp_val + center_bias  # maximize distance worst-case
            better = (best is None) or (val > bestv)

        if better:
            bestv = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]