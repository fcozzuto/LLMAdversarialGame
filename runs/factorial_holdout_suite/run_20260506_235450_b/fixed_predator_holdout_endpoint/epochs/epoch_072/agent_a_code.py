def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Deterministic tie-breaking: fixed move order; stable sort via tuple scoring.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Score: dominate opponent on near-term pickups; also prefer moving toward resources
        # that opponent isn't already overwhelmingly closer to.
        cur = 0
        best_my = 10**9
        best_opp = 10**9
        for tx, ty in res:
            my_d = manh(nx, ny, tx, ty)
            opp_d = manh(ox, oy, tx, ty)
            best_my = min(best_my, my_d)
            best_opp = min(best_opp, opp_d)

            # Immediate grab bonus
            if my_d == 0:
                cur += 1000
                # If opponent is also on it, still prefer immediate due to higher priority.
                cur += 50 if opp_d > 0 else 0

            # Competition advantage: positive if we are closer
            diff = opp_d - my_d
            cur += diff * 20

            # Penalize chasing resources where opponent is far closer (likely denial)
            if diff < -1:
                cur += diff * 8  # negative

            # Small preference for nearer overall pickups
            cur += max(0, 6 - my_d)

        # Encourage closing in generally and slightly discourage stalling unless best_.
        cur += max(0, 4 - best_my)
        if dx == 0 and dy == 0:
            cur -= 2
        # Keep deterministic by incorporating move itself in comparison key
        key = (-cur, dx, dy)  # maximize cur
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]]