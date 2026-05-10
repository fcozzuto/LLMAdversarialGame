def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    obset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    selfset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    oppset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    unclaimset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh(x, y):
        return [(x+dx, y+dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    def dist_to_center(x, y):
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        dx = x - cx
        dy = y - cy
        return dx*dx + dy*dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # If unclaimed exist, prioritize stealing/claiming; otherwise drift to center and expand within safe area.
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obset:
            continue

        val = 0.0
        # immediate territory value (entering opponent territory flips)
        if (nx, ny) in oppset:
            val += 140.0
        elif (nx, ny) in unclaimset:
            val += 70.0
        elif (nx, ny) in selfset:
            val += 20.0
        else:
            val += 10.0  # untracked but unblocked

        # prefer moving near opponent territory edges / unclaimed clusters
        nbs = neigh(nx, ny)
        adj_opp = 0
        adj_un = 0
        adj_obs = 0
        for x2, y2 in nbs:
            if not inb(x2, y2):
                continue
            if (x2, y2) in oppset:
                adj_opp += 1
            if (x2, y2) in unclaimset:
                adj_un += 1
            if (x2, y2) in obset:
                adj_obs += 1
        val += adj_opp * 18.0 + adj_un * 9.0
        val -= adj_obs * 6.0

        # discourage tight traps: look for a slight increase in openness
        openness = 0
        for x2, y2 in nbs:
            if inb(x2, y2) and (x2, y2) not in obset:
                openness += 1
        val += openness * 1.0

        # deterministic tie-breaker: prefer lower distance to center late in game, otherwise slightly hedge
        t = observation.get("turn_index", 0)
        center_weight = 0.8 + 0.6 * (t >= 40)
        val -= dist_to_center(nx, ny) * (0.015 * center_weight)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]