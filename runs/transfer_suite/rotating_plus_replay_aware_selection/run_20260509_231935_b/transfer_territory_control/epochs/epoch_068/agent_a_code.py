def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unclaimed_set.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        if unclaimed_set:
            # Prefer closest unclaimed (higher score => smaller distance)
            md = 10**18
            for ux, uy in unclaimed_set:
                d = (ux - nx) * (ux - nx) + (uy - ny) * (uy - ny)
                if d < md:
                    md = d
            val = -md
        else:
            # No unclaimed: approach opponent
            d = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            val = -d
        # Tie-break deterministically by direction order
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]