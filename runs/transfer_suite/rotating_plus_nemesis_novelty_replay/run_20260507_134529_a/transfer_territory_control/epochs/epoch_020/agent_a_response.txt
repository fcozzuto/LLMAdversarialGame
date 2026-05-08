def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick a target: expand toward nearby unclaimed while staying away from opponent pressure.
    if not unclaimed:
        targets = list(opp_terr) if opp_terr else [(ox, oy)]
    else:
        targets = list(unclaimed)
    if not targets:
        return [0, 0]

    frontier = self_terr if self_terr else {(sx, sy)}
    best_t = None
    best_tv = -10**18
    opp_pos = (ox, oy)
    for tx, ty in targets:
        dmin_self = 10**9
        for fx, fy in frontier:
            d = abs(tx - fx) + abs(ty - fy)
            if d < dmin_self:
                dmin_self = d
        d_opp = abs(tx - opp_pos[0]) + abs(ty - opp_pos[1])
        # Prefer reachable expansion (small self distance), and prefer areas not too close to opponent.
        tv = -dmin_self + 0.35 * d_opp
        if (tx, ty) in opp_terr:
            tv += 5
        if tv > best_tv:
            best_tv = tv
            best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = abs(nx - tx) + abs(ny - ty)
        d_to_opp = abs(nx - ox) + abs(ny - oy)

        v = -d_to_t  # head toward target
        if (nx, ny) in resources:
            v += 8
        if (nx, ny) in unclaimed:
            v += 3.5
        if (nx, ny) in opp_terr:
            # Flipping on entry is enabled; if we can counterclaim, do it decisively.
            v += 18
        # Prefer staying close to our existing territory to avoid easy counterclaims.
        if self_terr:
            dmin_st = 10**9
            for fx, fy in frontier:
                d = abs(nx - fx) + abs(ny - fy)
                if d < dmin_st:
                    dmin_st = d
            v += -0.35 * dmin_st
        # Avoid being too close to opponent unless we are flipping them.
        if (nx, ny) not in opp_terr:
            v += -0.06 * max(0, 6 - d_to_opp)

        if v > best_v or (v == best_v and (dx, dy) < best_move):
            best_v = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]