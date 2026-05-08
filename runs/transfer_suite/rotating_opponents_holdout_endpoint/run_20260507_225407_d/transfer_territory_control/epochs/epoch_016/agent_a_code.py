def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    resources = set((int(p[0]), int(p[1])) for p in (observation.get("resources") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    # Build a small "frontier pressure" map: count how exposed a cell is to opponent territory.
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_edge = set()
    for (px, py) in opp_terr:
        for dx, dy in neigh:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) not in opp_terr and (nx, ny) not in obstacles:
                opp_edge.add((nx, ny))

    # Prefer claiming safe unclaimed/resources and forming a buffer line away from opponent.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # If entering opponent territory, only do it when it also increases distance from opponent (trap avoidance).
        enter_opp = (nx, ny) in opp_terr
        enter_res = (nx, ny) in resources
        enter_un = (nx, ny) in unclaimed
        enter_self = (nx, ny) in self_terr
        exposed = (nx, ny) in opp_edge

        d_me = min((manh(nx, ny, ux, uy) for (ux, uy) in unclaimed), default=999)
        d_res = min((manh(nx, ny, rx, ry) for (rx, ry) in resources), default=999)
        d_opp = manh(nx, ny, ox, oy)

        # Favor being farther from opponent while reducing distance to unclaimed.
        score = 0
        score += (d_opp) * 8.0
        if enter_un:
            score += 1200.0
        if enter_res:
            score += 900.0 - 0.2 * d_res
        if enter_self:
            score += 50.0

        # Don't step into opponent territory unless it "pulls" us away.
        if enter_opp:
            score -= 600.0 + 6.0 * d_opp
        if exposed:
            score -= 180.0

        # Slight bias toward progressing along the diagonal away from the opponent corner.
        # (Start corners are opposite; pushing toward your side generally reduces contested flips.)
        diag_dir = 1 if ox < w // 2 else -1
        score += (nx - sx) * diag_dir * 10.0 + (ny - sy) * diag_dir * 10.0

        # Keep moves deterministic: stable tie-break by lexicographic (dx,dy).
        key = (score, -dx, -dy)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]