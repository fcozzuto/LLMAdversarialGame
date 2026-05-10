def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    x, y = observation.get("self_position") or [0, 0]
    x, y = int(x), int(y)

    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []

    self_set = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)
    blk = set((int(p[0]), int(p[1])) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp_adj = set()
    for ox, oy in opp_set:
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blk:
                opp_adj.add((nx, ny))
    targets = [c for c in un_set if c not in blk] or [c for c in opp_adj if c in un_set and c not in blk] or []

    def best_target_dist(px, py):
        if not targets:
            return 0
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - px) + abs(ty - py)
            if d < best:
                best = d
        return best

    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blk:
            continue
        gain = 0
        if (nx, ny) in un_set:
            gain += 7
        if (nx, ny) in opp_set:
            gain += 5
        if (nx, ny) in self_set:
            gain += 1
        dist = best_target_dist(nx, ny)
        edge = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge = 1
        # Prefer decreasing distance to unclaimed; slight preference for expanding.
        val = gain * 10 - dist + edge
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move