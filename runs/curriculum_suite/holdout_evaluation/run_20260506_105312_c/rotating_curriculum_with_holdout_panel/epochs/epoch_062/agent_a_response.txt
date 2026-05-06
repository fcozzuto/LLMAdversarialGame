def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def best_target():
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = int(r[0]), int(r[1])
            dS = dist(sx, sy, tx, ty)
            dO = dist(ox, oy, tx, ty)
            # Prefer resources where we are relatively closer (dO - dS larger).
            pr = (dO - dS, -dS, -tx, -ty)
            if best is None or pr > best[0]:
                best = (pr, tx, ty)
        return best[1], best[2] if best else (sx, sy)

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_target()

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dS2 = dist(nx, ny, tx, ty)
        dO2 = dist(ox, oy, tx, ty)
        # Also break ties deterministically by preferring lower "threat" to our advantage.
        key = (dS2, -(dO2 - dS2), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]