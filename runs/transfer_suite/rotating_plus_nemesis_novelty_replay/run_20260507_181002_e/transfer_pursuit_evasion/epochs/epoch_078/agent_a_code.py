def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def is_pursuer(role):
        r = str(role or "").lower()
        return ("pursuer" in r) or ("chaser" in r) or ("seeker" in r) or ("hunter" in r)

    self_p = is_pursuer(observation.get("self_role", ""))
    opp_p = is_pursuer(observation.get("opponent_role", ""))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def opp_best_move(ox0, oy0, sx1, sy1, opp_is_p):
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = ox0 + dx, oy0 + dy
            if not legal(nx, ny):
                continue
            dist = d2(nx, ny, sx1, sy1)
            val = -dist if opp_is_p else dist  # pursuer minimizes distance => maximize -dist
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best = (dx, dy)
                best_val = val
        return best if best is not None else (0, 0)

    best_move = (0, 0)
    best_val = None

    # If roles are missing/odd, default to pursuing.
    my_p = self_p if (self_p or opp_p) else True
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        odx, ody = opp_best_move(ox, oy, nx, ny, opp_p if (self_p or opp_p) else (not my_p))
        onx, ony = ox + odx, oy + ody
        dist = d2(nx, ny, onx, ony)
        val = -dist if my_p else dist  # pursuer tries to reduce distance; evader tries to increase
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]