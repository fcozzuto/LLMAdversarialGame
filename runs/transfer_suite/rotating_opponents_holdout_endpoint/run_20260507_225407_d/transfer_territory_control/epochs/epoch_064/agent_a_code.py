def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    nearest_un = None
    if unclaimed:
        xu, yu = min(unclaimed, key=lambda p: dist2(sx, sy, p[0], p[1]))
        nearest_un = (xu, yu)
    nearest_opp = None
    if opp_t:
        xo, yo = min(opp_t, key=lambda p: dist2(sx, sy, p[0], p[1]))
        nearest_opp = (xo, yo)

    best = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0
        if (nx, ny) in self_t:
            v += 1
        if (nx, ny) in unclaimed:
            v += 6
        if (nx, ny) in opp_t:
            v += 9  # flipping on entry
            # if we can immediately take opponent territory, weight more deterministically by how close it is to their bulk
            v += 0.1 * (1 + dist2(nx, ny, ox, oy) * 0 - 0)

        if nearest_un is not None:
            v += 3.0 / (1 + dist2(nx, ny, nearest_un[0], nearest_un[1]))
        if nearest_opp is not None:
            # pressure opponent: prefer moving toward their territory, but only slightly
            v += 1.3 / (1 + dist2(nx, ny, nearest_opp[0], nearest_opp[1]))

        # avoid stepping off our own captured region into the void if it doesn't improve
        if (nx, ny) not in self_t and (nx, ny) not in unclaimed and (nx, ny) not in opp_t:
            v -= 2

        if v > best or (v == best and (dx, dy) < best_move):
            best = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]