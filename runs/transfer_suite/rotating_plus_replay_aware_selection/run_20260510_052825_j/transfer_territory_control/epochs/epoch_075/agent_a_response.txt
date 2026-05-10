def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed = set((p[0], p[1]) for p in unclaimed if p is not None and len(p) >= 2)

    selfT = observation.get("self_territory") or []
    selfT = set((p[0], p[1]) for p in selfT if p is not None and len(p) >= 2)

    oppT = observation.get("opponent_territory") or []
    oppT = set((p[0], p[1]) for p in oppT if p is not None and len(p) >= 2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def dist_to_any(px, py, targets):
        if not targets: return 10**9
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - px) + abs(ty - py)
            if d < best: best = d
        return best

    def adj_frontier(px, py):
        # prefer moves that create contact with unclaimed to expand next
        best = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            nx, ny = px + dx, py + dy
            if (nx, ny) in unclaimed:
                best = max(best, 1)
            if (nx, ny) in oppT:
                best = max(best, 1)
        return best

    if not unclaimed and not oppT:
        return [0, 0]

    # Step-2 deterministic lookahead (greedy evaluation only)
    def eval_pos(px, py):
        if (px, py) in obstacles: return -10**12
        base = 0
        if (px, py) in unclaimed: base += 18
        if (px, py) in oppT: base += 8
        if (px, py) in selfT: base += 3
        base += adj_frontier(px, py) * 2
        # distance pressure toward nearest unclaimed; if none, toward opponent territory to counterclaim
        target_set = unclaimed if unclaimed else oppT
        d = dist_to_any(px, py, target_set)
        base -= d * 0.6
        return base

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = x, y
            dx, dy = 0, 0
        v1 = eval_pos(nx, ny)
        # one-step lookahead: choose best next move from that position (greedy)
        v2 = -10**18
        for dx2, dy2 in deltas:
            nnx, nny = nx + dx2, ny + dy2
            if not inb(nnx, nny) or (nnx, nny) in obstacles:
                nnx, nny = nx, ny
            val = eval_pos(nnx, nny)
            if val > v2: v2 = val
        val_total = v1 * 1.0 + v2 * 0.45
        if val_total > best_val:
            best_val = val_total
            best_move = (dx, dy)
        elif val_total == best_val:
            # deterministic tie-break: prefer diagonal expansion, then toward increasing x, then increasing y
            key1 = (abs(best_move[0]) + abs(best_move[1]) == 2, best_move[0], best_move[1])
            key2 = (abs(dx) + abs(dy) == 2, dx, dy)
            if key2 > key1:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]