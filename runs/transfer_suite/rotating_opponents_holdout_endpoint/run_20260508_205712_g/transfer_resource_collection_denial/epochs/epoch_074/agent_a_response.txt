def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    scored = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obs:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer resources where we are faster; tie-break with closer distance and stable ordering.
        scored.append((od - sd, -sd, -((rx + 3 * ry) % 7), rx, ry))
    if not scored:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    scored.sort(reverse=True)
    tx, ty = scored[0][3], scored[0][4]

    def best_step_toward(tx, ty):
        cand = []
        sdx = 0 if tx == sx else (1 if tx > sx else -1)
        sdy = 0 if ty == sy else (1 if ty > sy else -1)
        prefs = [(sdx, sdy), (sdx, 0), (0, sdy), (sdx, -sdy), (-sdx, sdy), (0, 0)]
        for dx, dy in prefs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                # Score by resulting distance to target; small deterministic bias to prefer diagonals.
                dist = md(nx, ny, tx, ty)
                diag_bonus = 0 if (dx == 0 or dy == 0) else -0.01
                cand.append((dist + diag_bonus, -(dx * dy), dx, dy))
        # If preferred directions blocked, fall back to any legal move that reduces distance.
        if not cand:
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny):
                    continue
                cand.append((md(nx, ny, tx, ty) + (0.001 if dx == 0 and dy == 0 else 0), 0, dx, dy))
        cand.sort()
        return [cand[0][2], cand[0][3]]

    return best_step_toward(tx, ty)