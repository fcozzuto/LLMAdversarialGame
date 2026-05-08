def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in srole) or ("chase" in srole) or ("seeker" in srole) or ("catch" in srole)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def corner_score(x, y):
        # distance to nearest corner (larger is better for evader, smaller is better for pursuer)
        md = 10**9
        for cx, cy in corners:
            d = abs(x - cx) + abs(y - cy)
            if d < md: md = d
        return md

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            nx, ny = sx, sy  # engine would keep in place on invalid move

        d = cheb(nx, ny)
        if is_pursuer:
            # also prefer moves that reduce cornering distance to opposite corner of evasion
            # (evader_corner tends to hide in corners; going toward its current corner helps)
            opp_corner_near = min(abs(ox - cx) + abs(oy - cy) for cx, cy in corners)
            score = d * 10 + (opp_corner_near * 0.1)
            better = (best_score is None) or (score < best_score)
        else:
            # flee: maximize distance from pursuer and move toward farthest corner
            score = -d * 10 - corner_score(nx, ny)
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]