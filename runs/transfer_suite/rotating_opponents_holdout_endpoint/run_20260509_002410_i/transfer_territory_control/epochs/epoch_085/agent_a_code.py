def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cells_from_list(lst):
        out = []
        for p in lst or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    out.append((x, y))
        return out

    resources = cells_from_list(observation.get("resources"))
    unclaimed = cells_from_list(observation.get("unclaimed_cells"))
    if not resources:
        resources = unclaimed

    if resources:
        targets = resources
    else:
        # No clear target: push toward opponent position/territory.
        opp_terr = cells_from_list(observation.get("opponent_territory"))
        targets = opp_terr if opp_terr else [(ox, oy)]

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_opp = dist((nx, ny), (ox, oy))
        d_t = min(dist((nx, ny), t) for t in targets)
        # Prefer decreasing distance to target while also getting closer to opponent.
        score = (-(d_t * 2) - d_opp) + (0 if (dx, dy) != (0, 0) else -1)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]