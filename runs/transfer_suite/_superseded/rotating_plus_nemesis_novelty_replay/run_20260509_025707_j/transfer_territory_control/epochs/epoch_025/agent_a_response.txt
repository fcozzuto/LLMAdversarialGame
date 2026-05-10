def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def count_adj(cset, x, y):
        c = 0
        for dx, dy in neigh8:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in cset:
                c += 1
        return c

    def cell_score(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in self_cells:
            return 3.0
        d_opp = abs(nx - ox) + abs(ny - oy)
        if (nx, ny) in opp_cells:
            # Prefer flipping opponent territory but not suicidally into blocked choke points.
            return 100.0 - 0.9 * d_opp - 2.0 * count_adj(self_cells, nx, ny)
        if (nx, ny) in unclaimed:
            adj_opp = count_adj(opp_cells, nx, ny)
            adj_self = count_adj(self_cells, nx, ny)
            # Expand our safe frontier first; then challenge opponent borders deterministically.
            edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            return (12.0 * adj_self + 2.0 * (3 - d_opp // 2) + 8.0 * adj_opp
                    - 3.5 * max(0, adj_opp - adj_self) + (2.0 if edge else 0.0) - 0.05 * d_opp)
        # Other cells: treat as neutral/undesirable
        return -50.0 - 0.2 * abs(nx - sx) - 0.2 * abs(ny - sy)

    best = None
    best_s = -10**18
    # Deterministic tie-break order as given in neigh8 (including stay)
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        s = cell_score(nx, ny)
        if s > best_s:
            best_s = s
            best = (dx, dy)

    return [best[0], best[1]]