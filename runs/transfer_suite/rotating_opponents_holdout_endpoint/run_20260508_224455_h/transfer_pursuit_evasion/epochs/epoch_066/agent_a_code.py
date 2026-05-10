def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            if isinstance(p, dict) and "x" in p and "y" in p:
                x, y = int(p["x"]), int(p["y"])
            else:
                continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    role = str(observation.get("self_role") or observation.get("role") or "").lower()
    evader = ("evader" in role) or ("escape" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best_dx, best_dy = 0, 0
    best_val = None
    ti = int(observation.get("turn_index") or 0)

    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist = cheb(nx, ny, ox, oy)
        # Escape-option count (prefer positions with more legal moves)
        opts = 0
        for j, (adx, ady) in enumerate(moves):
            tx, ty = nx + adx, ny + ady
            if valid(tx, ty):
                opts += 1
        # Obstacle proximity penalty (avoid hugging obstacles too tightly)
        prox = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) in obs:
                prox += 1

        # Deterministic tiebreak using move index + turn index
        tiebreak = (i * 37 + ti) % 1000

        # Evader maximizes distance; pursuer minimizes distance.
        if evader:
            val = dist * 100 + opts * 3 - prox * 2 + tiebreak * 1e-6
        else:
            val = -dist * 100 + opts * 3 - prox * 2 - tiebreak * 1e-6

        if best_val is None or val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]