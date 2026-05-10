def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < W and 0 <= y < H

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def toset(lst):
        s = set()
        for p in lst or []:
            if p and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    myT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    unSet = toset(observation.get("unclaimed_cells"))

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    neigh = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy)]
    dirs = neigh + [(0, 0)]

    def adj_to(tset, x, y):
        for dx, dy in neigh:
            if (x + dx, y + dy) in tset:
                return True
        return False

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would reject, but keep deterministic

        val = 0
        if (nx, ny) in unSet:
            val += 6
        if (nx, ny) in oppT:
            val += 10
        if (nx, ny) in myT:
            val += 1

        if (nx, ny) in unSet and adj_to(myT, nx, ny):
            val += 4  # frontier expansion
        if (nx, ny) in unSet and adj_to(oppT, nx, ny):
            val += 3  # blocking opponent edge

        # Prefer moving away from opponent while still expanding
        opp_dist = max(1, abs(nx - ox) + abs(ny - oy))
        val += 0.2 * opp_dist

        center_dist = abs(nx - cx) + abs(ny - cy)
        val -= 0.05 * center_dist

        # Deterministic tie-break: fixed order dirs
        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    return best