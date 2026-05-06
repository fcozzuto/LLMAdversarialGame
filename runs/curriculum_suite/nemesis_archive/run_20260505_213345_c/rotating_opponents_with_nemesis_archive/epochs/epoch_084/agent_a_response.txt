def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Choose target: prefer resources where we are closer, and where we don't give opponent an easy race.
    best_t = resources[0]
    best_val = -10**9
    opp_row = oy
    for r in resources:
        dm = dist8((sx, sy), r)
        do = dist8((ox, oy), r)
        row_pen = 2 if r[1] == opp_row else 0
        # If opponent is closer, heavily penalize; still allow if it's very close to us.
        race = do - dm
        val = (race * 10) - row_pen * 3 - dm
        if (r[0] + r[1]) % 2 == 0:
            val += 0.5  # tiny deterministic tie-break
        if val > best_val:
            best_val = val
            best_t = r

    tx, ty = best_t
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Greedy step to reduce distance to target while avoiding obstacles; also discourage moving into a cell
    # that makes opponent closer to our target than we are.
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dm_next = dist8((nx, ny), (tx, ty))
        do_now = dist8((ox, oy), (tx, ty))
        # assume opponent can match best step; approximate with one-step reduction potential
        # by checking the best among its immediate neighbors (deterministic, no recursion).
        opp_best = do_now
        for pdx, pdy in dirs:
            ex, ey = ox + pdx, oy + pdy
            if inside(ex, ey):
                opp_best = min(opp_best, dist8((ex, ey), (tx, ty)))
        threat = (opp_best - dm_next)
        score = (-dm_next * 3) + (threat * 5)  # prefer keeping/creating advantage over opponent
        # prefer matching target row/col alignment progression to reduce Z-shaped stagnation
        if ty != ny:
            score += 0.2
        if (nx + ny) % 2 == 0:
            score += 0.1
        # small bias to avoid standing still unless no better
        if dx == 0 and dy == 0:
            score -= 0.3
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]