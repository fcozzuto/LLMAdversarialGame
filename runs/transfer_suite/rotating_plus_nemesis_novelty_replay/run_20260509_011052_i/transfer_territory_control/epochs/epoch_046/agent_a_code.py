def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_target():
        for key in ("resources", "unclaimed_cells"):
            cells = observation.get(key, []) or []
            if cells:
                return min((int(p[0]), int(p[1])) for p in cells)
        return None

    target = best_target()
    if target is None:
        # If no explicit targets, chase opponent deterministically
        target = (ox, oy)

    tx, ty = target

    best = None
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if best_d is None or d < best_d:
            best_d = d
            best = [dx, dy]
    if best is not None:
        return best

    # Fallback: any valid step (or stay)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]