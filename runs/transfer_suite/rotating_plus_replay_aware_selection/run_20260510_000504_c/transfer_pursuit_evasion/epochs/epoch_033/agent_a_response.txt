def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    if not ("purs" in self_role or "chase" in self_role):
        if ("purs" in opp_role) or ("chase" in opp_role):
            i_am_evader = True
        elif ("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role):
            i_am_evader = False

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def nearest_corner_d2(x, y):
        best = None
        for cx, cy in corners:
            d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Greedy with obstacle-friendly tie-breakers.
        if i_am_evader:
            val = dist2(nx, ny)  # maximize distance
            # Strongly prefer corners unless heavily blocked around.
            val += 0.15 * (w * h - nearest_corner_d2(nx, ny))
            # Slightly prefer moves that keep mobility.
            mobility = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if valid(tx, ty):
                    mobility += 1
            val += 0.02 * mobility
            # Avoid positions that are adjacent to many obstacle boundaries (softly).
            edge_pen = 0
            for ddx, ddy in [(1,0),(-1,0),(0,1),(0,-1)]:
                if not valid(nx + ddx, ny + ddy):
                    edge_pen += 1
            val -= 0.01 * edge_pen
            better = best_val is None or val > best_val
        else:
            val = -dist2(nx, ny)  # minimize distance
            # If roles are pursuer, also prefer moving toward the evader.
            val -= 0.01 * nearest_corner_d2(nx, ny)  # don't camp corners as pursuer
            # Prefer higher mobility to avoid getting stuck behind obstacles.
            mobility = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if valid(tx, ty):
                    mobility += 1
            val += 0.02 * mobility
            edge_pen = 0
            for ddx, ddy in [(1,0),(-1,0),(0,1),(0,-1)]:
                if not valid(nx + ddx, ny + ddy):
                    edge_pen += 1
            val -= 0.005 * edge_pen
            better = best_val is None or val > best_val

        if better:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]