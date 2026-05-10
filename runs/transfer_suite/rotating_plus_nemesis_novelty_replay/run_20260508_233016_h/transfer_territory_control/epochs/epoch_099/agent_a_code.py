def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    candidates = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 0), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in selfT:
            return -1  # discourage wandering back
        # Prefer claiming/unclaimed; prefer stealing opponent; consider proximity to both
        base = 0
        if (nx, ny) in unclaimed:
            base += 40
        if (nx, ny) in oppT:
            base += 90  # flipping on entry
        if (nx, ny) in obstacles:
            base -= 10**9

        # Reward adjacency to our territory to grow efficiently; punish if too close to opponent
        adj_self = 0
        adj_opp = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                xx, yy = nx + dx, ny + dy
                if not inb(xx, yy):
                    continue
                if (xx, yy) in selfT:
                    adj_self += 1
                if (xx, yy) in oppT:
                    adj_opp += 1
        base += adj_self * 6
        base += adj_opp * 4

        # Balance: move toward opponent to create pressure, but don't suicide into their densest region
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_to_mid = abs(nx - w // 2) + abs(ny - h // 2)
        base += (14 - d_to_opp) * 1.2
        base += (12 - d_to_mid) * 0.3
        return base

    best = None
    best_s = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        s = score_cell(nx, ny)
        # If equal, choose deterministic tie-break toward minimizing distance to opponent
        if s > best_s or (s == best_s and (abs(nx - ox) + abs(ny - oy), abs(nx - sx) + abs(ny - sy), nx, ny) <
                           (abs((best[0] if best else sx) - ox) + abs((best[1] if best else sy) - oy), 0, 0, 0)):
            best_s = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]