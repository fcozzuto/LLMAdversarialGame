def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    obstacles = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources", []) or []
    resources = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]

    def legal_moves():
        moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    moves.append((dx, dy))
        return moves

    legal = legal_moves()
    if not legal:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If already on a resource, stop; else move toward nearest resource.
    resset = set(resources)
    if (sx, sy) in resset:
        return [0, 0]

    if resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # Prefer immediate resource; then minimize distance to it.
            d = min(manh(nx, ny, rx, ry) for rx, ry in resources)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # No resources known: move toward opponent.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = manh(nx, ny, ox, oy)
        if best is None or d < best[0]:
            best = (d, dx, dy)
    return [best[1], best[2]]