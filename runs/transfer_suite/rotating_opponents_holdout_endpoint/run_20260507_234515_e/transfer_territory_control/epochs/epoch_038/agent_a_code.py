def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def norm_cells(key):
        out = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = norm_cells("obstacles")
    resources = norm_cells("resources")
    unclaimed = norm_cells("unclaimed_cells")
    selfT = norm_cells("self_territory")
    oppT = norm_cells("opponent_territory")

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = neigh

    # Choose target: nearest resource, else nearest unclaimed adjacent to our territory, else center-ish
    if resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        frontier = set()
        if selfT:
            for x, y in selfT:
                for dx, dy in neigh:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                        frontier.add((nx, ny))
        if frontier:
            tx, ty = min(frontier, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        elif unclaimed:
            tx, ty = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        else:
            tx, ty = w // 2, h // 2

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Deterministic heuristic: go closer to target; also try not to approach opponent too much if tied
        d = abs(nx - tx) + abs(ny - ty)
        v = (d, abs(nx - ox) + abs(ny - oy))
        if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        # Fallback: try stay, else first legal neighbor by fixed order
        if (sx, sy) not in obstacles:
            return [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]