def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "")).lower()
    i_am_pursuer = ("pursuer" in role) or ("pursur" in role)

    obst = set()
    for p in observation.get("obstacles", []):
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def opp_best_after(me_nx, me_ny, oppx, oppy):
        # Opponent pursues directly: picks move that minimizes distance to our next position
        bestd = None
        best = (0, 0)
        for dx, dy in deltas:
            nx, ny = oppx + dx, oppy + dy
            if not legal(nx, ny):
                continue
            d = dist2(nx, ny, me_nx, me_ny)
            if bestd is None or d < bestd or (d == bestd and (dx, dy) < best):
                bestd, best = d, (dx, dy)
        return best

    # One-ply robust lookahead
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        odx, ody = opp_best_after(nx, ny, ox, oy)
        onx, ony = ox + odx, oy + ody
        d = dist2(nx, ny, onx, ony)
        # If we're pursuer: maximize our own distance reduction => minimize distance after opponent move (they chase our next)
        # If we're evader: maximize distance after opponent move.
        score = -d if i_am_pursuer else d
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]