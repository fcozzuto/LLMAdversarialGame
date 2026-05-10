def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    self_role = observation.get("self_role", "") or ""
    opp_role = observation.get("opponent_role", "") or ""

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def dist(x1, y1, x2, y2):
        # Use Manhattan as in typical env; diagonal allowed but we score with manhattan.
        return abs(x1 - x2) + abs(y1 - y2)

    # Heuristic role guess: whichever contains "pursuer"/"evader"
    me_pursuer = ("pursuer" in self_role.lower()) or ("pursuit" in self_role.lower())
    if not (me_pursuer or ("evader" in self_role.lower())):
        # Fallback: assume we are pursuer by default in pursuit_evasion.
        me_pursuer = True

    def best_step_from(px, py, tx, ty, maximize):
        best = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            v = dist(nx, ny, tx, ty)
            if bestv is None:
                bestv = v
                best = (dx, dy)
                continue
            if maximize:
                if v > bestv or (v == bestv and (dx, dy) < best):
                    bestv = v
                    best = (dx, dy)
            else:
                if v < bestv or (v == bestv and (dx, dy) < best):
                    bestv = v
                    best = (dx, dy)
        return best

    if me_pursuer:
        # Predict evader move: maximize distance from us
        ev_step = best_step_from(ox, oy, sx, sy, maximize=True)
        tx, ty = ox + ev_step[0], oy + ev_step[1]
        # Move to minimize distance to predicted evader
        my_step = best_step_from(sx, sy, tx, ty, maximize=False)
        return [int(my_step[0]), int(my_step[1])]
    else:
        # Predict pursuer move: minimize distance to us
        pu_step = best_step_from(sx, sy, ox, oy, maximize=False)
        px, py = sx + pu_step[0], sy + pu_step[1]
        # Move to maximize distance from predicted pursuer position
        my_step = best_step_from(sx, sy, px, py, maximize=True)
        return [int(my_step[0]), int(my_step[1])]