def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_cell = (sx, sy)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny) or (nx, ny) == (ox, oy):
            continue

        # For this candidate cell, consider the best resource we could race for now.
        # Key: maximize advantage (opp_dist - self_dist), then minimize our distance, then prefer ending closer to any resource.
        cell_best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            key = (adv, -sd, -man(nx, ny, rx, ry) + 0)  # keep sd as primary, adv as primary
            if cell_best is None or key > cell_best:
                cell_best = key
        key = cell_best
        # Tie-break deterministically by coordinates
        if best_key is None or key > best_key or (key == best_key and (nx, ny) < best_cell):
            best_key = key
            best_cell = (nx, ny)

    bx, by = best_cell
    return [bx - sx, by - sy]