def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    role = observation.get("self_role", "pursuer")
    deltas = [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If we are evader, run directly away while respecting obstacles.
    if role == "evader":
        best = (0, 0)
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = dist2(nx, ny, ox, oy)
            if (nx + ny) % 2 != (sx + sy) % 2:
                v -= 1  # keep parity stable (deterministic tie-break)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pursuer: 1-step minimax with a cutoff/anti-drift term.
    # Generate possible opponent moves given its current position.
    opp_cands = []
    for dx, dy in deltas:
        px, py = ox + dx, oy + dy
        if inb(px, py):
            opp_cands.append((px, py))
    if not opp_cands:
        opp_cands = [(ox, oy)]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if nx == ox and ny == oy:
            return [dx, dy]

        # assume opponent moves to maximize our distance next turn
        worst_dist = -1
        for px, py in opp_cands:
            d = dist2(nx, ny, px, py)
            if d > worst_dist:
                worst_dist = d

        # anti-drift: prefer moves that reduce current distance and keep parity with opponent
        cur = dist2(nx, ny, ox, oy)
        parity = -1 if (nx + ny) % 2 != (ox + oy) % 2 else 0

        # value: maximize negative worst_dist, i.e., minimize worst_dist; plus strong current-distance pull
        val = -worst_dist - 4 * cur + parity
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]