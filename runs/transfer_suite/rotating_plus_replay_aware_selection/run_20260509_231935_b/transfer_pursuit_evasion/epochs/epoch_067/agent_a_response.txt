def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("evader" not in self_role and "pursuer" not in opp_role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def best_opponent_step():
        # Assume opponent moves to maximize distance from us (ties broken deterministically).
        best = None
        bestd = None
        for dx, dy in deltas:
            nx, ny = ox + dx, oy + dy
            if not legal(nx, ny):
                continue
            d = dist2(nx, ny, sx, sy)
            if best is None or d > bestd or (d == bestd and (nx, ny) < best):
                best = (nx, ny)
                bestd = d
        return best if best is not None else (ox, oy)

    tx, ty = (ox, oy)
    if i_am_pursuer:
        tx, ty = best_opponent_step()
        # Move toward predicted opponent step while avoiding obstacles; avoid increasing distance to it.
        best_move = (0, 0)
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = dist2(nx, ny, tx, ty)
            # Primary: minimize distance to target. Secondary: also reduce current distance to actual opponent.
            v2 = dist2(nx, ny, ox, oy)
            key = (v, v2, nx, ny)
            if best_val is None or key < best_val:
                best_val = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # Evader: move to maximize distance from pursuer while avoiding obstacles.
        best_move = (0, 0)
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            # Secondary: prefer moves that also move away in x then y deterministically.
            key = (-v, -abs(nx - ox), -abs(ny - oy), nx, ny)
            if best_val is None or key < best_val:
                best_val = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]