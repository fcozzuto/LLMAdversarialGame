def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    cx, cy = (w - 1) // 2, (h - 1) // 2

    opp_list = list(opp_terr)
    def min_dist_to_opp(x, y):
        md = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < md:
                md = d
        return md if opp_list else (abs(ox - x) + abs(oy - y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dcenter = abs(nx - cx) + abs(ny - cy)
        dtop = min_dist_to_opp(nx, ny)
        if (nx, ny) in self_terr:
            v = 1.0 - 0.08 * dcenter + 0.02 * dtop
        elif (nx, ny) in opp_terr:
            v = 3.5 - 0.07 * dcenter + 0.03 * dtop
        elif (nx, ny) in unclaimed:
            v = 4.2 - 0.09 * dcenter + 0.06 * dtop
        else:
            v = 2.0 - 0.08 * dcenter + 0.02 * dtop
        if best is None or v > bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]