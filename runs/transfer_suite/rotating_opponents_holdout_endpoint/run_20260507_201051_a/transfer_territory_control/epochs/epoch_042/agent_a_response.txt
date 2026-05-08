def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    adj8 = [(-1, -1), (0, -1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
    moves = adj8 + [(0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def has_adj(tset, x, y):
        for dx, dy in adj8:
            if (x + dx, y + dy) in tset:
                return True
        return False

    def min_dist2_to_set(x, y, tset):
        md = None
        for tx, ty in tset:
            d = (x - tx) * (x - tx) + (y - ty) * (y - ty)
            if md is None or d < md:
                md = d
        return 10**9 if md is None else md

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = [0, 0]
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        is_un = (nx, ny) in unclaimed
        is_self = (nx, ny) in self_t
        is_opp = (nx, ny) in opp_t

        sc = 0
        if is_un:
            sc += 10
        elif is_self:
            sc += 4
        elif is_opp:
            sc += 14  # flipping on entry is enabled

        if has_adj(unclaimed, nx, ny):
            sc += 3  # likely expand next
        if has_adj(self_t, nx, ny):
            sc += 2  # keep connected
        if has_adj(opp_t, nx, ny):
            sc -= 1  # avoid being hemmed in unless we can flip now
        if is_opp:
            sc += 2 * (min_dist2_to_set(nx, ny, unclaimed) == 10**9)

        d_opp = min_dist2_to_set(nx, ny, opp_t)
        d_self = min_dist2_to_set(nx, ny, self_t)
        sc += 1.2 * (d_self == 0)  # staying on owned territory is safe
        sc += 2.5 / (1 + d_opp)   # approach opponent frontier to enable flips/denial

        # moderate center pressure
        sc += -0.08 * (((nx - cx) * (nx - cx)) + ((ny - cy) * (ny - cy)))

        # break ties deterministically: prefer lexicographically smallest move among equal scores
        if sc > best_sc or (sc == best_sc and (dx, dy) < tuple(best_move)):
            best_sc = sc
            best_move = [dx, dy]

    return best_move