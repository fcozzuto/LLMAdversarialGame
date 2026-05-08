def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()
    i_am_pursuer = (("pursuer" in srole) or ("chaser" in srole) or ("catch" in srole) or ("pursuit" in srole))
    if "evader" in srole or "evad" in srole:
        i_am_pursuer = False
    if (("pursuer" in orole) or ("chaser" in orole) or ("catch" in orole) or ("pursuit" in orole)):
        i_am_pursuer = False

    candidates = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not candidates:
        return [0, 0]

    def dist2(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    ncx, ncy = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    # Evader tends to corners: pursuer uses an intercept point just "inside" the corner direction.
    ix = ox + (ox - ncx)
    iy = oy + (oy - ncy)
    ix = 0 if ix < 0 else (w - 1 if ix > w - 1 else ix)
    iy = 0 if iy < 0 else (h - 1 if iy > h - 1 else iy)

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                m += 1
        return m

    best = None
    bestv = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if i_am_pursuer:
            d = dist2(nx, ny, ox, oy)
            di = dist2(nx, ny, ix, iy)
            v = -d - 0.2 * di + 0.05 * mobility(nx, ny)
        else:
            d = dist2(nx, ny, ox, oy)
            # Prefer moving away from pursuer while keeping mobility.
            v = d + 0.05 * mobility(nx, ny) - 0.01 * dist2(nx, ny, ncx, ncy)
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]