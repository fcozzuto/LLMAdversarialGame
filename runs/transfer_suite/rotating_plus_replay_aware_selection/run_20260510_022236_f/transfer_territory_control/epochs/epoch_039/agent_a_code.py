def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    my_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    cx, cy = w // 2, h // 2

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cell_score(x, y):
        if (x, y) in obs or not (0 <= x < w and 0 <= y < h):
            return -10**9
        base = 0
        if (x, y) in opp_terr:
            base += 60
        elif (x, y) in unclaimed:
            base += 22
        elif (x, y) in my_terr:
            base += 4

        adj_my = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if (nx, ny) in my_terr:
                adj_my = 1
                break
        base += 12 * adj_my
        base += - (abs(x - cx) + abs(y - cy)) * 0.25
        return base

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        val = cell_score(nx, ny)
        key = (val, -abs(dx) - abs(dy), -dx, -dy)
        if val > best_val or (val == best_val and best is not None and key > best):
            best_val = val
            best = key
            best_move = [dx, dy]
    return best_move