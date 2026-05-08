def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if not (dx == 0 and dy == 0):
                dirs.append((dx, dy))
    dirs.append((0, 0))

    def legal_from(x, y):
        out = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                out.append((dx, dy))
        return out if out else [(0, 0)]

    my_moves = legal_from(sx, sy)
    opp_moves = legal_from(ox, oy)

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_val = None  # we minimize max distance

    for mdx, mdy in my_moves:
        nsx, nsy = sx + mdx, sy + mdy
        worst = -1
        capture_found = False
        for odx, ody in opp_moves:
            nox, noy = ox + odx, oy + ody
            if nsx == nox and nsy == noy:
                capture_found = True
                worst = 0
                break
            d = dist2(nsx, nsy, nox, noy)
            if d > worst:
                worst = d
        if capture_found:
            val = -10**12
        else:
            val = worst
        if best_val is None or val < best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]