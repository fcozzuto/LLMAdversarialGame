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

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def best_opponent_move(myx, myy, ex, ey):
        # opponent assumes maximizes distance (if evading), or minimizes (if pursuer mirror)
        maximize = not pursuer
        best = None
        bestv = None
        for dx, dy in deltas:
            nx, ny = ex + dx, ey + dy
            if not legal(nx, ny):
                continue
            v = dist2(myx, myy, nx, ny)
            if maximize:
                if bestv is None or v > bestv:
                    bestv, best = v, (dx, dy)
                elif v == bestv and (dx, dy) < best:
                    best = (dx, dy)
            else:
                if bestv is None or v < bestv:
                    bestv, best = v, (dx, dy)
                elif v == bestv and (dx, dy) < best:
                    best = (dx, dy)
        return best if best is not None else (0, 0)

    # deterministic preferred direction (intercept style)
    ax = 0 if ox == sx else (1 if ox > sx else -1)
    ay = 0 if oy == sy else (1 if oy > sy else -1)
    preferred = (ax, ay)

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        candidates.append((dx, dy))
    candidates.sort(key=lambda m: (m != preferred, dist2(sx + m[0], sy + m[1], ox, oy)))

    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx == ox and ny == oy:
            return [dx, dy]

        # anticipate opponent response from their perspective
        odx, ody = best_opponent_move(nx, ny, ox, oy)
        onx, ony = ox + odx, oy + ody

        # if we're pursuer, minimize distance after opponent moves; else maximize
        v = dist2(nx, ny, onx, ony)
        if pursuer:
            key = v
            if best_val is None or key < best_val or (key == best_val and (dx, dy) < best_move):
                best_val, best_move = key, (dx, dy)
        else:
            key = -v
            if best_val is None or key > best_val or ((-v) == best_val and (dx, dy) < best_move):
                best_val, best_move = key, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]