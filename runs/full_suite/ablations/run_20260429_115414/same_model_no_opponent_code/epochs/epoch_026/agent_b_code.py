def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))

    def dist(a, b, c, d):
        # Chebyshev-like for diagonal friendliness
        ad = abs(a - c)
        bd = abs(b - d)
        return ad if ad > bd else bd

    if not moves:
        return [0, 0]

    if resources:
        # Pick a resource where we have the best distance advantage over opponent.
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Prefer being closer; then maximize opponent distance.
            key = (myd - opd, myd, -(rx + ry))
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)

        rx, ry = best_r
        best_m = None
        best_s = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            myd2 = dist(nx, ny, rx, ry)
            opd2 = dist(ox, oy, rx, ry)
            # Also steer slightly away from being too close to opponent (avoid contesting if even).
            oppd = dist(nx, ny, ox, oy)
            s = (-myd2) + (0.15 * opd2) + (0.03 * oppd)
            if best_s is None or s > best_s:
                best_s = s
                best_m = (dx, dy)
        return [int(best_m[0]), int(best_m[1])]

    # No resources: move to a deterministic "frontier" point near opponent.
    # If we are on the same side along x/y, push diagonally toward opponent's corner.
    tx = 0 if ox > sx else w - 1
    ty = 0 if oy > sy else h - 1
    best_m = None
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = dist(nx, ny, tx, ty)
        # Tie-break deterministically by preferring moves that progress in x then y toward target.
        bx = -abs((tx - nx))
        by = -abs((ty - ny))
        key = (d, -bx, -by)
        if best_d is None or key < best_d:
            best_d = key
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]