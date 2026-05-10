def choose_move(observation):
    x, y = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target_cells = list(unclaimed) + list(opp_terr)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def md(a, b):
        d = a - b
        return d if d >= 0 else -d

    def manhattan(px, py, qx, qy):
        return md(px, qx) + md(py, qy)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        if (nx, ny) in opp_terr:
            gain = 50
        elif (nx, ny) in unclaimed:
            gain = 20
        elif (nx, ny) in self_terr:
            gain = 3
        else:
            gain = 1

        penalty_obs = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obstacles:
                penalty_obs -= 8

        if target_cells:
            # Prefer moves that reduce distance to the closest high-value cell (unclaimed or enemy territory)
            best_dist = 10**9
            for tx, ty in target_cells:
                d = manhattan(nx, ny, tx, ty)
                if d < best_dist:
                    best_dist = d
            dist_term = -best_dist
        else:
            # No explicit frontier: drift toward center
            dist_term = -(manhattan(nx, ny, int(round(cx)), int(round(cy))) )

        # Tie-break deterministically: prefer larger x then larger y (lexicographic on move)
        key = (-(gain + dist_term + penalty_obs), -gain, -dist_term, penalty_obs, -nx, -ny)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best