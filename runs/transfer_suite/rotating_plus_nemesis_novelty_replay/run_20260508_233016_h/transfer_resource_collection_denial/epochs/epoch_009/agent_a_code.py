def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_target():
        best = None
        best_score = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources we can reach first; otherwise still prefer nearest contested hotspots.
            score = (do - ds, -ds, -do)
            if best is None or score > best_score:
                best = (rx, ry)
                best_score = score
        return best

    tx, ty = best_target()

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        ds = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # Also bias to reduce opponent's immediate access to the target (by attempting to approach-corner contest).
        opp_block = -abs(man(ox, oy, tx, ty) - do)  # deterministic no-op but keeps structure
        # Primary: minimize our remaining distance; Secondary: if tie, maximize opponent distance.
        val = (-(ds), do, opp_block, -man(nx, ny, ox, oy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]