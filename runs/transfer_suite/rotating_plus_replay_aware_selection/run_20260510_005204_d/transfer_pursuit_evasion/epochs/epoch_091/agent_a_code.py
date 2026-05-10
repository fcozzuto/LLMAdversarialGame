def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_grad(x, y):
        # Penalize being adjacent to obstacles (except if blocked already).
        if (x, y) in blocked:
            return 10**9
        pen = 0
        for bx, by in blocked:
            d2 = dist2(x, y, bx, by)
            if d2 == 1:
                pen += 3
            elif d2 == 2:
                pen += 1
        return pen

    # Small heuristic: pursue/pivot to break zigzag by favoring moves that align with opponent's position.
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d2 = dist2(nx, ny, ox, oy)
        og = obstacle_grad(nx, ny)

        # Prefer moves that either capture (pursuer) or maximize escape distance (evader).
        # Add mild mobility and alignment.
        mobility = 0
        for mdx, mdy in moves:
            tx, ty = nx + mdx, ny + mdy
            if free(tx, ty):
                mobility += 1

        align = abs((nx - sx) - (ox - sx)) + abs((ny - sy) - (oy - sy))
        # align is zero only for exact delta match; used as a deterministic small tie-break.

        if is_evader:
            val = (d2, mobility, -align, -og, -nx, -ny)
        else:
            # Minimize distance; if ties, maximize mobility, avoid obstacles, then deterministic preference.
            val = (-d2, mobility, -og, align, nx, ny)

        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    if best is None:
        return [0, 0]
    return best