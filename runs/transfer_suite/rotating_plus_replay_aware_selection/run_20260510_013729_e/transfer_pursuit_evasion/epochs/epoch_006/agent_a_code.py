def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    ob = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    self_is_evader = ("evader" in role)
    opp_is_evader = not self_is_evader

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in ob

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_opponent_step(xo, yo, myx, myy):
        best = None
        # Opponent tries to maximize distance if evader, else minimize.
        for dx, dy in deltas:
            nx, ny = xo + dx, yo + dy
            if not valid(nx, ny):
                continue
            d = manh(nx, ny, myx, myy)
            key = d if opp_is_evader else -d
            # Tie-break: if same outcome, prefer moving away/toward in x then y to stay deterministic.
            axis = (abs(nx - xo), abs(ny - yo))
            tieb = axis if opp_is_evader else (-axis[0], -axis[1])
            cand = (key, tieb, dx, dy)
            if best is None or cand > best:
                best = cand
        if best is None:
            return 0, 0
        return best[2], best[3]

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # One-ply minimax: our move, then opponent chooses best response.
        odx, ody = best_opponent_step(ox, oy, nx, ny)
        nox, noy = ox + odx, oy + ody
        if not valid(nox, noy):
            nox, noy = ox, oy
        d_after = manh(nx, ny, nox, noy)

        # If we are evader, maximize distance; if pursuer, minimize worst-case distance.
        score = d_after if self_is_evader else -d_after
        # Tie-break: slightly prefer larger progress along changing axis to avoid dithering.
        axis = (abs(nx - sx), abs(ny - sy))
        tieb = axis if self_is_evader else (-axis[0], -axis[1])
        cand = (score, tieb, dx, dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]