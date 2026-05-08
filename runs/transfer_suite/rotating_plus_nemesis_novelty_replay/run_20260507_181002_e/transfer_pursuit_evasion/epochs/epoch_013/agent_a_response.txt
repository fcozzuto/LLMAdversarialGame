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

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in dirs:
            if free(x + dx, y + dy):
                c += 1
        return c

    my_moves = legal_from(sx, sy)
    opp_moves = legal_from(ox, oy)

    best_move = my_moves[0]
    best_val = None

    for mdx, mdy in my_moves:
        nsx, nsy = sx + mdx, sy + mdy
        worst_for_me = -10**18
        for odx, ody in opp_moves:
            nox, noy = ox + odx, oy + ody
            # Opponent wants maximize distance; tie-break with their escape potential via our mobility.
            val = dist2(nsx, nsy, nox, noy) - 0.12 * mobility(nsx, nsy)
            if val > worst_for_me:
                worst_for_me = val
        # Prefer lower worst-case distance; tie-break by higher mobility and closer to opponent.
        tie = (dist2(nsx, nsy, ox, oy), mobility(nsx, nsy))
        if best_val is None or worst_for_me < best_val or (worst_for_me == best_val and (tie[0], -tie[1]) < (best_tie[0], best_tie[1])):
            best_move = [mdx, mdy]
            best_val = worst_for_me
            best_tie = (tie[0], -tie[1])

    return best_move