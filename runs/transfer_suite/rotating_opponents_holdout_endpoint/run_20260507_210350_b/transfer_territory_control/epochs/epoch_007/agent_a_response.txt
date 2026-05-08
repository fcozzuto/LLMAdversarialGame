def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def to_set(v):
        s = set()
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    s.add((int(p[0]), int(p[1])))
        return s

    self_set = to_set(observation.get("self_territory"))
    opp_set = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    if not (0 <= sx < w and 0 <= sy < h):
        sx, sy = 0, 0

    def adj_to(sset, x, y):
        for dx, dy in dirs:
            if (x + dx, y + dy) in sset:
                return True
        return False

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        target_is_self = (nx, ny) in self_set
        target_is_opp = (nx, ny) in opp_set
        target_is_un = (nx, ny) in unclaimed

        # Frontier metrics
        near_self = adj_to(self_set, nx, ny)
        near_opp = adj_to(opp_set, nx, ny)
        near_obs = adj_to(blocked, nx, ny)

        # Tactical distance shaping
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_to_center = abs(nx - centerx) + abs(ny - centery)

        # Claim value
        v = 0.0
        if target_is_self:
            v += 6.0
        elif target_is_un:
            v += 16.0
        elif target_is_opp:
            # Flipping on entry, but also risk of immediate counterclaim
            v += 14.0
            v += 5.0 if near_self else 0.0

        if near_self:
            v += 10.0
        if near_opp:
            v += 3.0 if target_is_opp or target_is_un else -2.0

        v += 1.5 * d_to_opp
        v -= 0.5 * d_to_center
        if near_obs:
            v -= 4.0

        # Mild preference to keep moving away from opponent position when unclaimed exists
        if target_is_un:
            v += 0.25 * d_to_opp

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]