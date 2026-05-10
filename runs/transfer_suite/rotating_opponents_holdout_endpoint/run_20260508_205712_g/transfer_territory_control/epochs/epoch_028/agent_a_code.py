def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = moves

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def count_unclaimed_nbr(x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                c += 1
        return c

    # Focus on contesting opponent expansion: prefer stepping onto/near opponent frontier, while keeping distance control.
    best_score = -10**18
    best = (0, 0)
    dmin_opp = 10**9
    for ax, ay in opp_terr:
        d = cheb_dist(sx, sy, ax, ay)
        if d < dmin_opp:
            dmin_opp = d

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        to_opp = cheb_dist(nx, ny, ox, oy)
        on_opp = 1 if (nx, ny) in opp_terr else 0

        # If move touches/attacks opponent edge, prioritize strongly.
        near_opp_unclaimed = 0
        for ddx, ddy in neigh:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in opp_terr and (ax, ay) in opp_terr:
                pass
            if (ax, ay) in opp_terr:
                near_opp_unclaimed += 1

        # Compute local expansion potential: adjacency to unclaimed.
        exp = count_unclaimed_nbr(nx, ny)

        # Avoid getting too close to likely edge-trapping: lightly prefer staying more central than opponent when behind.
        central = min(nx, w - 1 - nx, ny, h - 1 - ny)
        opp_central = min(ox, w - 1 - ox, oy, h - 1 - oy)
        central_bias = 0.2 * (central - opp_central)

        # Deterministic tie-break: prefer lexicographically earlier moves.
        score = 3.5 * on_opp + 0.35 * near_opp_unclaimed + 1.2 * exp - 0.6 * to_opp + 0.05 * central_bias
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]