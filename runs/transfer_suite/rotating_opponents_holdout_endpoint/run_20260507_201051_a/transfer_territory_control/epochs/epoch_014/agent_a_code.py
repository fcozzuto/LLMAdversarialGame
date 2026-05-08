def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_t:
            gain = 0.0
        elif (nx, ny) in opp_t:
            gain = 6.0
        elif (nx, ny) in unclaimed:
            gain = 2.0
        else:
            gain = 0.5

        # Reward moves that push toward far-from-center expansion (edges), not center fighting.
        dist_edge = abs(nx - cx) + abs(ny - cy)
        # Slightly prefer grabbing cells adjacent to our territory to grow safely.
        adj_own = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in self_t:
                    adj_own += 1
        # If capturing opponent territory, also prefer if it borders many unclaimed cells (potential flip spread).
        adj_un = 0
        if (nx, ny) in opp_t:
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    tx, ty = nx + ax, ny + ay
                    if (tx, ty) in unclaimed:
                        adj_un += 1

        score = (gain * 100.0 + dist_edge * 3.0 + adj_own * 1.2 + adj_un * 0.8, -dx, -dy, nx, ny)
        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort()
    return [int(cand[0][1]), int(cand[0][2])]