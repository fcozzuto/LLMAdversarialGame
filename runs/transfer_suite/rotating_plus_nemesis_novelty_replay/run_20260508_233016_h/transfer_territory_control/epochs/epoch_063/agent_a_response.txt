def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # Build deterministic prioritized targets:
    # 1) unclaimed cells adjacent to opponent territory (likely to counterclaim)
    # 2) remaining unclaimed
    # 3) otherwise, move toward center
    targets = []
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_edge = set()
    for ex, ey in oppT:
        for dx, dy in neigh:
            nx, ny = ex + dx, ey + dy
            if inb(nx, ny) and (nx, ny) not in oppT and (nx, ny) not in selfT:
                opp_edge.add((nx, ny))
    if opp_edge:
        targets.extend([t for t in sorted(opp_edge) if t in unclaimed][:20] or sorted(list(opp_edge))[:20])
    if not targets and unclaimed:
        targets.extend(sorted(unclaimed)[:28])
    if not targets:
        targets = [(w // 2, h // 2)]

    def score_cell(x, y):
        # Prefer immediate claim threat: entering opponent territory flips; entering edge-like cells helps.
        if (x, y) in obstacles: return -10**9
        base = 0
        if (x, y) in oppT: base += 5000
        if (x, y) in unclaimed: base += 120
        if (x, y) in selfT: base -= 5
        # Move toward best target by deterministic distance and bias away from opponent when not forcing
        best = 10**9
        for tx, ty in targets:
            d = man(x, y, tx, ty)
            # Also bias toward reducing opponent's distance to our target area
            do = man(x, y, tx, ty)
            d2 = man(ox, oy, tx, ty)
            best = min(best, d * 2 + d2)
        base += 100 - best
        # Mild obstacle/edge stability: keep within bounds and away from obstacles
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in obstacles:
                base -= 15
        return base

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break: smaller (dx,dy) lexicographically
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        val = score_cell(nx, ny)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]