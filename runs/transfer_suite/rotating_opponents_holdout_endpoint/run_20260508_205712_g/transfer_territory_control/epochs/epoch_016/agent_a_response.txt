def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles", []) or []) if 0 <= int(x) < w and 0 <= int(y) < h)
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []) if 0 <= int(x) < w and 0 <= int(y) < h)
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []) if 0 <= int(x) < w and 0 <= int(y) < h)
    unC = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []) if 0 <= int(x) < w and 0 <= int(y) < h)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def neigh(x, y):
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny): yield nx, ny

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if not selfT:
        # fallback: go to center
        tx = 0 if sx == int(cx) else (1 if sx < int(cx) else -1)
        ty = 0 if sy == int(cy) else (1 if sy < int(cy) else -1)
        return [tx, ty]

    best = None
    best_sc = -10**9
    # fixed iteration order gives deterministic tie-breaking
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            sc = -10**8 if (nx, ny) != (sx, sy) else -1
        else:
            sc = 0.0
            if (nx, ny) in selfT: sc += 1.2
            if (nx, ny) in unC: sc += 2.1
            if (nx, ny) in oppT: sc += 6.0  # flipping on entry is enabled
            # frontier-ish behavior
            adj_self = adj_opp = adj_un = 0
            for ax, ay in neigh(nx, ny):
                if (ax, ay) in selfT: adj_self += 1
                elif (ax, ay) in oppT: adj_opp += 1
                elif (ax, ay) in unC: adj_un += 1
            sc += 0.35 * adj_self
            sc += 0.20 * adj_un
            sc -= 0.45 * adj_opp  # avoid pushing into opponent clusters unless we actually flip
            # steer toward center slightly to avoid getting stuck on edges
            sc -= 0.03 * (abs(nx - cx) + abs(ny - cy))
            # if we're not adjacent to any self territory, still allow unclaimed capture
            if adj_self == 0 and (nx, ny) not in selfT: sc -= 0.35

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]