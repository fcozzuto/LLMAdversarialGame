def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_list = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obs_list)

    unclaimed_list = observation.get("unclaimed_cells", []) or []
    unclaimed = [(int(x), int(y)) for x, y in unclaimed_list]

    self_terr_list = observation.get("self_territory", []) or []
    self_terr = set((int(x), int(y)) for x, y in self_terr_list)

    opp_terr_list = observation.get("opponent_territory", []) or []
    opp_terr = set((int(x), int(y)) for x, y in opp_terr_list)

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose an expansion target: prefer unclaimed adjacent to our territory,
    # and also far from opponent (to reduce immediate flip leverage).
    candidates = []
    if unclaimed:
        if self_terr:
            for tx, ty in unclaimed:
                if any((tx + dx, ty + dy) in self_terr for dx, dy in neigh8 if (dx, dy) != (0, 0)):
                    candidates.append((tx, ty))
        if not candidates:
            candidates = unclaimed

    if not candidates:
        return [0, 0]

    best = None
    best_score = -10**18
    for tx, ty in candidates:
        if (tx, ty) in obs:
            continue
        d_me = dist(sx, sy, tx, ty)
        d_opp = dist(ox, oy, tx, ty)
        # If opponent territory exists, bias away from it by using nearest opposite cell distance.
        if opp_terr:
            d_opp_terr = 10**9
            for px, py in opp_terr:
                dd = dist(tx, ty, px, py)
                if dd < d_opp_terr:
                    d_opp_terr = dd
            d_opp = min(d_opp, d_opp_terr + 1)
        score = (d_me * -1) + (d_opp * 3) - (1 if (tx, ty) in self_terr else 0)
        # Encourage moving to cells that are also far from obstacles implicitly by preferring fewer blocked neighbors.
        score -= sum(1 for dx, dy in neigh8 if (dx or dy) and inb(tx + dx, ty + dy) and (tx + dx, ty + dy) in obs) * 0.25
        if score > best_score or (score == best_score and (tx, ty) < best):
            best_score = score
            best = (tx, ty)

    tx, ty = best
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Main: move toward chosen target. Secondary: keep away from opponent.
        val = -dist(nx, ny, tx, ty) + dist(nx, ny, ox, oy) * 1.2
        # Slightly prefer diagonals if they reduce distance similarly.
        if dx != 0 and dy != 0:
            val += 0.05
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move