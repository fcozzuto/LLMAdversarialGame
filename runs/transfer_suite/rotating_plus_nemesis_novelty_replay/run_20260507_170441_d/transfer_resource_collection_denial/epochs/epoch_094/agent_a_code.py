def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def d(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        # Deterministic denial: move to reduce space near opponent's corner
        tx, ty = (w - 1, h - 1) if sx + sy <= ox + oy else (0, 0)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -d(nx, ny, tx, ty) - 0.1 * d(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # For each move: pick the resource that is best for us from the resulting cell,
    # then score by advantage over opponent in contesting it.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Find our preferred target from (nx, ny)
        best_r = None
        best_rd = 10**9
        for rx, ry in resources:
            sd = d(nx, ny, rx, ry)
            if sd < best_rd:
                best_rd = sd
                best_r = (rx, ry)
        rx, ry = best_r

        my_dist = d(nx, ny, rx, ry)
        opp_dist = d(ox, oy, rx, ry)

        # Encourage denying: approach a resource closer than opponent; otherwise move to reduce our own lead.
        lead = opp_dist - my_dist
        # Slightly prefer moving toward opponent-side direction to disrupt their routes.
        toward_opp_corner = (d(nx, ny, w - 1, h - 1) - d(sx, sy, w - 1, h - 1)) * 0.01
        v = lead * 1000 - my_dist * 3 - toward_opp_corner

        # If we can collect immediately, add large deterministic boost.
        if my_dist == 0:
            v += 10**6

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]