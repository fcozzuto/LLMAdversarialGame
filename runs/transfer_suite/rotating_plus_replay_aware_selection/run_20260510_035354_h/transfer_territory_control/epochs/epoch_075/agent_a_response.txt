def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    obset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    ucell = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    uset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    oset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    center = (w / 2.0 - 0.5, h / 2.0 - 0.5)
    # distance from a point to nearest cell in set (Manhattan, with safe fallback)
    def nearest_dist(pt, s):
        if not s:
            return 10**9
        x, y = pt
        return min(abs(x - sx) + abs(y - sy) for (sx, sy) in s)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = -10**18

    # If we can flip opponent cells now, prioritize it heavily.
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        val = 0.0
        p = (nx, ny)

        if p in oset:
            val += 500.0  # immediate flip on entry is very valuable
        if p in ucell:
            val += 18.0  # claiming unclaimed territory
        if p in uset:
            val -= 1.0  # slight penalty: prefer expansion

        # Prefer moving toward contested / opponent area
        val -= 0.9 * nearest_dist(p, oset)
        # Prefer expanding toward center (helps maintain lead against counterclaim patterns)
        val -= 0.15 * (abs(nx - center[0]) + abs(ny - center[1]))

        # Avoid stepping onto "dead ends" when opponent is close: if opponent adjacent, encourage.
        # (Compute quick local adjacency)
        adj_opp = 0
        for ddx, ddy in ((1,0),(-1,0),(0,1),(0,-1)):
            q = (nx + ddx, ny + ddy)
            if q in oset:
                adj_opp += 1
        val += 6.0 * adj_opp

        # If we have no nearby targets in unclaimed, still move to reduce distance to opponent.
        if not ucell and not oset:
            val += 0.01 * (-(abs(nx - center[0]) + abs(ny - center[1])))

        # Deterministic tie-break: fixed move order already; use strict > then == by order.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]