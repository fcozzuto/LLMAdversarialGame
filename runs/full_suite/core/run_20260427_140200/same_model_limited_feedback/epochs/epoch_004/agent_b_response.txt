def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    res_set = set(tuple(p) for p in resources)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_res_dist(x, y):
        if not resources:
            return 0
        md = 10**9
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if d < md:
                md = d
        return md

    def blocked(x, y):
        return (x, y) in obstacles

    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            score = -10**12
        else:
            # Prefer stepping onto a resource.
            score = 0.0
            if (nx, ny) in res_set:
                score += 10000.0
            # Prefer moving toward the nearest remaining resource.
            score += -2.0 * nearest_res_dist(nx, ny)
            # Mildly prefer increasing distance from opponent unless we are threatening a resource.
            score += -0.25 * (abs(nx - ox) + abs(ny - oy))
            # Slightly prefer center-ish to avoid corner traps.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score += -0.01 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # Deterministic tie-break: consistent ordering by deltas list.
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]