def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def cells(key):
        out = set()
        for p in observation.get(key) or []:
            if p is None:
                continue
            if isinstance(p, dict):
                continue
            if len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obs = cells("obstacles")
    res = cells("resources")
    unclaimed = cells("unclaimed_cells")
    if not unclaimed:
        unclaimed = cells("unclaimed")

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    selfT = cells("self_territory")
    oppT = cells("opponent_territory")

    def best_towards(targets):
        if not targets:
            return None
        best = None
        bestd = 10**18
        for nx, ny in neigh_cells:
            if (nx, ny) in obs:
                continue
            d = min((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty) for tx, ty in targets)
            if d < bestd:
                bestd = d
                best = (nx, ny)
        return best

    neigh_cells = [(sx + dx, sy + dy) for dx, dy in neigh]
    neigh_cells = [(x, y) for (x, y) in neigh_cells if 0 <= x < w and 0 <= y < h and (x, y) not in obs]

    if res:
        targets = res
        nxt = best_towards(targets)
        if nxt is not None:
            return [nxt[0] - sx, nxt[1] - sy]

    if selfT and unclaimed:
        frontier = set()
        for x, y in selfT:
            for dx, dy in neigh:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed and (nx, ny) not in obs:
                    frontier.add((nx, ny))
        nxt = best_towards(frontier) if frontier else None
        if nxt is not None:
            return [nxt[0] - sx, nxt[1] - sy]

    if oppT and unclaimed:
        targets = (oppT & unclaimed) or (oppT | unclaimed)
        nxt = best_towards(targets) if targets else None
        if nxt is not None:
            return [nxt[0] - sx, nxt[1] - sy]

    if unclaimed:
        targets = unclaimed
        nxt = best_towards(targets)
        if nxt is not None:
            return [nxt[0] - sx, nxt[1] - sy]

    if neigh_cells:
        dx, dy = neigh_cells[0][0] - sx, neigh_cells[0][1] - sy
        if dx in (-1, 0, 1) and dy in (-1, 0, 1):
            return [dx, dy]

    return [0, 0]