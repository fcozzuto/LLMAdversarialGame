def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = (observation.get("opponent_position") or (W - 1, H - 1))
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))
        except Exception:
            pass

    selfT = set()
    for p in (observation.get("self_territory") or []):
        try:
            selfT.add((int(p[0]), int(p[1])))
        except Exception:
            pass
    oppT = set()
    for p in (observation.get("opponent_territory") or []):
        try:
            oppT.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        try:
            unclaimed.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    def centrality(x, y):
        dx = (x - cx)
        dy = (y - cy)
        # higher is better (closer to center)
        return 8.0 - (dx * dx + dy * dy)

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in selfT:
            return -1.0  # don't waste moves on own territory
        base = 2.0 if (x, y) in unclaimed else 1.0  # prefer unclaimed, then flipping opponent
        d_me = abs(x - sx) + abs(y - sy)
        d_opp = abs(x - ox) + abs(y - oy)
        # push away from opponent while moving toward center
        return base * 5.0 + centrality(x, y) + 0.15 * d_opp - 0.9 * d_me

    # immediate lookahead: choose best neighbor cell by heuristic
    best = (-10**18, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            x, y = sx + dx, sy + dy
            if not (0 <= x < W and 0 <= y < H):
                continue
            v = cell_value(x, y)
            # small bias to keep moving (avoid standing still unless tied)
            if dx == 0 and dy == 0:
                v -= 0.05
            if v > best[0]:
                best = (v, dx, dy)

    return [int(best[1]), int(best[2])]