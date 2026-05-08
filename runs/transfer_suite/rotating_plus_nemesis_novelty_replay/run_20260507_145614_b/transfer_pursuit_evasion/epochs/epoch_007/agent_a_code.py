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

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    # Deterministic tie-break order: already in deltas
    if i_am_pursuer:
        best_move = [0, 0]
        best_score = None  # lower is better (minimax worst-case distance)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            if nx == ox and ny == oy:
                return [dx, dy]
            worst = -1
            for odx, ody in deltas:
                mx, my = ox + odx, oy + ody
                if not legal(mx, my):
                    continue
                if mx == nx and my == ny:
                    # opponent would be caught; treat as worst for them
                    d = -1
                else:
                    d = dist2(nx, ny, mx, my)
                if d > worst:
                    worst = d
            if worst < 0:
                worst = 0
            if best_score is None or worst < best_score:
                best_score = worst
                best_move = [dx, dy]
        return best_move
    else:
        best_move = [0, 0]
        best_score = None  # higher is better (minimax worst-case distance after opponent pursues)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # If we allow opponent to land on us immediately, that's losing; minimize that via minimax.
            worst = 10**18
            for odx, ody in deltas:
                mx, my = ox + odx, oy + ody
                if not legal(mx, my):
                    continue
                if mx == nx and my == ny:
                    d = 0
                else:
                    d = dist2(nx, ny, mx, my)
                # opponent (pursuer) will minimize our distance, so worst-case for us = min distance
                if d < worst:
                    worst = d
            if best_score is None or worst > best_score:
                best_score = worst
                best_move = [dx, dy]
        return best_move