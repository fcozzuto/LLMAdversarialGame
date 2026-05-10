def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    # New strategy: "opportunistic denier": prioritize resources where we can arrive no later than opponent,
    # and among those prefer ones that opponent is already close to (so we steal first).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        s = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If we move closer, add denier/steal value; also slightly reward lowering our own distance.
            steal = (opd - myd)  # positive => we can race better
            s += (1000 if (nx == rx and ny == ry) else 0) + steal * 3 - myd

        # Tie-break: prefer moves that don't run away from opponent's nearest threatened resource
        # (creates decisive direction changes vs previous policy).
        if s > best_score:
            best_score = s
            best = (dx, dy)

    return [int(best[0]), int(best[1])]