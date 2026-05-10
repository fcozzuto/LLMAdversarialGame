def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def to_set(key):
        pts = observation.get(key) or []
        s = set()
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    s.add((int(p[0]), int(p[1])))
                except:
                    pass
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_ter = to_set("self_territory")

    op = observation.get("opponent_position") or sp
    ox, oy = int(op[0]), int(op[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        on_unclaimed = 1 if (nx, ny) in unclaimed else 0
        adj_self = 1 if self_ter and any((nx + adx, ny + ady) in self_ter for adx, ady in ((-1,0),(1,0),(0,-1),(0,1))) else 0
        dist_opp = abs(nx - ox) + abs(ny - oy)
        # Prefer unclaimed, then adjacency to our territory, then minimize distance to opponent, then deterministic tie-break
        key = (on_unclaimed, adj_self, -dist_opp, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]