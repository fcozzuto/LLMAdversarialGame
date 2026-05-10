def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    opp_corner_x, opp_corner_y = (w - 1, h - 1) if (sx, sy) == (0, 0) else (0, 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_unclaimed(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                c += 1
        return c

    def nearest_unclaimed_dist(x, y):
        # small deterministic local scan; prefer proximity without full-grid search
        best = 10**9
        for ax in (-2, -1, 0, 1, 2):
            for ay in (-2, -1, 0, 1, 2):
                nx, ny = x + ax, y + ay
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                    d = abs(nx - x) + abs(ny - y)
                    if d < best:
                        best = d
        return best if best != 10**9 else None

    best_move = (0, 0)
    best_score = -10**18

    # Encourage capturing along the frontier; also avoid getting boxed by preferring cells
    # that increase our adjacency to unclaimed and reduce opponent adjacency.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_terr:
            score += 18  # flipping on entry is valuable
        elif (nx, ny) in unclaimed:
            score += 12
        elif (nx, ny) in self_terr:
            score += 3

        score += 2 * adj_unclaimed(nx, ny)

        # penalize moving closer to opponent territory blobs unless it is a direct flip
        if (nx, ny) not in opp_terr:
            # local estimate of opponent proximity
            opp_adj = 0
            for ox, oy in ((-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2),
                          (-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)):
                tx, ty = nx + ox, ny + oy
                if (tx, ty) in opp_terr:
                    opp_adj += 1
            score -= 1.5 * opp_adj

        # deterministic preference: advance toward opponent corner (territory_center_claim tends inward)
        score += -0.01 * (abs(nx - opp_corner_x) + abs(ny - opp_corner_y))

        # if current move reaches unclaimed nearby, slightly prefer smaller distance
        nd = nearest_unclaimed_dist(nx, ny)
        if nd is not None:
            score += 0.5 * (5 - nd)

        # small tie-break: prefer non-staying unless equal
        if (dx, dy) == (0, 0):
            score -= 0.05

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # fixed ordering tie-break to stay deterministic
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]