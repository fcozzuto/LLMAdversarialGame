def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed_list = observation.get("unclaimed_cells") or observation.get("unclaimed") or []
    unclaimed = set(tuple(p) for p in unclaimed_list)
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    nearest_unc = None
    if unclaimed_list:
        nearest_unc = min(unclaimed_list, key=lambda p: (manh(sx, sy, p[0], p[1]), manh(ox, oy, p[0], p[1]), p[0], p[1]))

    best_val = -10**18
    best = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue

        dist_to_opp = manh(nx, ny, ox, oy)
        val = 0

        if (nx, ny) in selfT:
            val += 8
        if (nx, ny) in oppT:
            val += 180 + dist_to_opp  # strong counterclaim
        if (nx, ny) in unclaimed:
            val += 240

        if nearest_unc is not None:
            cu = manh(sx, sy, nearest_unc[0], nearest_unc[1])
            nu = manh(nx, ny, nearest_unc[0], nearest_unc[1])
            val += (cu - nu) * 25  # move toward nearest unclaimed

        if (nx, ny) in selfT:
            # keep options open: avoid walking into tight opponent reach
            val -= manh(nx, ny, ox, oy) * 0.5

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best