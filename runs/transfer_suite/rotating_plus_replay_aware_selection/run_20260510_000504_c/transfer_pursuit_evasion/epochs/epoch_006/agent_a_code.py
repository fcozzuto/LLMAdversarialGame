def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = (observation.get("self_role", "") or "").lower()

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist2(x, y, x2, y2):
        dx = x - x2
        dy = y - y2
        return dx * dx + dy * dy

    def freedom(x, y):
        c = 0
        for dx, dy in deltas:
            if valid(x + dx, y + dy):
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def farthest_corner_score(x, y):
        best = -1
        for cx, cy in corners:
            d = dist2(cx, cy, x, y)
            if d > best:
                best = d
        return best

    pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role) or ("pursuer" in role)
    best = None
    bestv = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_self_opp = dist2(nx, ny, ox, oy)
        f = freedom(nx, ny)
        corner_far = farthest_corner_score(nx, ny)
        # Wall-run adaptation:
        # - As pursuer, prefer moves that reduce distance and avoid giving the evader many exits.
        # - As evader, prefer moves that increase distance and head toward farthest corner.
        if pursuer:
            v = (-d_self_opp) + 0.35 * f - 0.05 * corner_far
            # extra deterministic bias to keep moving "toward" opponent
            v += 0.01 * (-(abs((nx - ox)) + abs((ny - oy))))
        else:
            v = (-d_self_opp) + 0.45 * f + 0.06 * corner_far
            # as evader, strongly prefer increasing distance
            v += 0.02 * (abs(nx - ox) + abs(ny - oy))

        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]