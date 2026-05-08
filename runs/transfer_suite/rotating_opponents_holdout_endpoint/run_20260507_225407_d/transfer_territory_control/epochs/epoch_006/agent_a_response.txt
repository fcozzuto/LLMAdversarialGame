def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", [sx, sy])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_cells = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_cells = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    unclaimed_list = list(unclaimed)
    if unclaimed_list:
        pass
    else:
        unclaimed_list = [tuple(observation.get("unclaimed_cells") or [ox, oy])][0:1]  # deterministic fallback

    dirs = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_s = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        if cell in opp_cells:
            gain = 3.2
        elif cell in unclaimed:
            gain = 2.0
        elif cell in self_cells:
            gain = 1.0
        else:
            gain = 0.0

        if unclaimed:
            # Prefer reducing distance to closest unclaimed; also bias toward unclaimed near opponent
            # to break center-claim patterns.
            best_du = None
            for ux, uy in unclaimed_list:
                d = md(nx, ny, ux, uy)
                if best_du is None or d < best_du:
                    best_du = d
            du = best_du if best_du is not None else 99
        else:
            du = md(nx, ny, ox, oy)

        # Avoid walking directly into opponent if not flipping (still deterministic via cell membership above)
        hate_opp = 0.0 if cell in opp_cells else 0.02 * md(nx, ny, ox, oy)

        # Prefer moving toward unclaimed and away from obstacles by keeping moves that are "more central"
        center_bias = -0.001 * md(nx, ny, 3.5, 3.5)

        s = gain * 10 - du * 1.1 - hate_opp + center_bias
        if best_s is None or s > best_s or (s == best_s and (dx, dy) < best):
            best_s = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]