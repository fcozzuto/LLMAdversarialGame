def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    my_adj = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_adj = my_adj

    def adj_to(s, x, y, adj):
        for dx, dy in adj:
            if (x + dx, y + dy) in s:
                return True
        return False

    # If opponent is very close, prioritize taking unclaimed tiles adjacent to us.
    center = (w - 1) / 2.0, (h - 1) / 2.0
    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in my:
            score = -1000
        else:
            score = 0
        in_un = (nx, ny) in un
        adj_my = adj_to(my, nx, ny, my_adj)
        adj_opp = adj_to(opp, nx, ny, opp_adj)
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_ctr = abs(nx - center[0]) + abs(ny - center[1])

        if in_un:
            score += 120
        if adj_my:
            score += 70
        if (nx, ny) in opp:
            score += 35  # entering enemy can flip territory
        if adj_opp:
            score -= 60
        # Keep some distance from opponent territory to avoid being swept
        score += min(60, d_opp * 6)
        # Prefer moves that progress outward from our start direction
        score -= d_ctr * 1.5

        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]