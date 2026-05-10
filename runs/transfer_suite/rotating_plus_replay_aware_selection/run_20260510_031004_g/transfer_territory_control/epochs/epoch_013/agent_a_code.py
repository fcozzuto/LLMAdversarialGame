def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = set(map(tuple, observation.get("resources", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_resource_dist(x, y):
        if not resources:
            return 10**9
        dmin = None
        for rx, ry in resources:
            dd = abs(rx - x) + abs(ry - y)
            if dmin is None or dd < dmin:
                dmin = dd
        return dmin if dmin is not None else 10**9

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    has_resources = bool(resources)
    best = None
    for dx, dy, nx, ny in candidates:
        dres = best_resource_dist(nx, ny)
        dopp = abs(nx - px) + abs(ny - py)
        # Prefer resources; if none, pressure opponent. Deterministic tie-break via tuple order.
        score = (0 if has_resources else 1, dres if has_resources else dopp, dopp)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]