def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" in self_role and "evader" not in self_role)
    if "pursuer" in self_role and "evader" not in self_role:
        is_evader = False

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx*dx + dy*dy

    # Score: evader maximize distance; pursuer minimize distance.
    # Small 2-step lookahead: anticipate opponent's best response to our move.
    best_move = (0, 0)
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy and is_evader:
            continue

        # Predict opponent move: deterministic best response from its perspective.
        # If we are evader, opponent likely pursues; if we are pursuer, opponent likely evades.
        opp_moves = moves
        opp_best_d = None
        for pdx, pdy in opp_moves:
            ax, ay = ox + pdx, oy + pdy
            if not ok(ax, ay):
                continue
            if is_evader:
                # opponent pursuer reduces our distance
                d = (ax - nx) * (ax - nx) + (ay - ny) * (ay - ny)
                if opp_best_d is None or d < opp_best_d:
                    opp_best_d = d
            else:
                # opponent evader increases our distance
                d = (ax - nx) * (ax - nx) + (ay - ny) * (ay - ny)
                if opp_best_d is None or d > opp_best_d:
                    opp_best_d = d

        if opp_best_d is None:
            opp_best_d = dist2(nx, ny)

        # Primary objective: distance after both move.
        val = opp_best_d
        # Tie-break: prefer moves that also keep away from boundaries for evader, and toward center for pursuer.
        boundary_pen = abs((nx == 0) - (nx == w - 1)) + abs((ny == 0) - (ny == h - 1))
        center_pen = abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)

        if is_evader:
            val = val * 100 - boundary_pen * 2
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        else:
            val = val * 100 + center_pen * 0.01
            if val < best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]