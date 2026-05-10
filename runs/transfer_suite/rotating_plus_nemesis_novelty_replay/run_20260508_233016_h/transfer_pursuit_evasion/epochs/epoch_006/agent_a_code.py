def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" in opp_role and "evad" not in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def clearance(x, y):
        if not obs:
            return 9
        md = 999
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md

    def corner_score(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            moves.append((nx, ny, dx, dy))

    if not moves:
        return [0, 0]

    best = None
    best_key = None
    for nx, ny, dx, dy in moves:
        dist = abs(nx - ox) + abs(ny - oy)
        clr = clearance(nx, ny)
        cs = corner_score(nx, ny)
        # If pursuer: minimize dist; if evader: maximize dist.
        # Tie-break: prefer staying away from obstacles and avoiding being pushed into corners (evader) / toward edges (pursuer).
        if pursuer:
            key = (dist, -clr, cs)
        else:
            key = (-dist, -clr, -cs)

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]