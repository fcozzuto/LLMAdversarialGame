def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        # No resources: drift toward opponent cautiously
        dx = 0
        dy = 0
        if ox > sx: dx = 1
        elif ox < sx: dx = -1
        if oy > sy: dy = 1
        elif oy < sy: dy = -1
        if (sx + dx, sy + dy) in obstacles: return [0, 0]
        return [dx, dy]

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    best = None
    best_key = None
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate by best resource "grab advantage" vs opponent
        cand = -10**18
        for rx, ry in resources:
            ds = dist2(nx, ny, rx, ry)
            do = dist2(ox, oy, rx, ry)
            # Higher means opponent is farther than we are; slight pressure to move closer
            val = (do - ds) - 0.05 * ds
            if val > cand:
                cand = val
        # Small tie-breakers: avoid moving away from opponent too much; prefer progress on resources
        opp_d = dist2(nx, ny, ox, oy)
        key = (cand, -opp_d, -abs(dx) - abs(dy))
        if best is None or key > best_key:
            best = (dx, dy)
            best_key = key

    if best is None:
        return [0, 0]
    return [best[0], best[1]]