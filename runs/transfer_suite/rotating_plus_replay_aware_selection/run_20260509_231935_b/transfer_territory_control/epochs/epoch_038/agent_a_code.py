def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index", 0)) % 9
    dirs = dirs[ti:] + dirs[:ti]

    # Precompute target distances for quick heuristic
    opp_list = list(opp_terr)
    un_list = list(unclaimed)

    def mind_to(cells, x, y):
        if not cells:
            return 99
        best = 10**9
        for px, py in cells:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    d_un_self = mind_to(un_list, sx, sy)
    d_opp_self = mind_to(opp_list, sx, sy)

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        v = 0.0
        if (nx, ny) in self_terr:
            v += 2.0
        if (nx, ny) in unclaimed:
            v += 5.0
        if (nx, ny) in opp_terr:
            v += 9.0

        v += (d_un_self - mind_to(un_list, nx, ny)) * 1.8
        v += (d_opp_self - mind_to(opp_list, nx, ny)) * 1.1

        # Center bias to counter "territory_center_claim"
        v += (abs(sx - cx) + abs(sy - cy) - (abs(nx - cx) + abs(ny - cy))) * 0.6

        # Nudge away from obstacles by penalizing steps adjacent to obstacles
        adj = 0
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                adj += 1
        v -= adj * 0.35

        # Deterministic tie-break: prefer smaller dx, then dy, then earlier in dirs
        key = (dx, dy)
        if v > best[1] or (v == best[1] and (best[0] is None or key < best[0])):
            best = ((dx, dy), v)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]