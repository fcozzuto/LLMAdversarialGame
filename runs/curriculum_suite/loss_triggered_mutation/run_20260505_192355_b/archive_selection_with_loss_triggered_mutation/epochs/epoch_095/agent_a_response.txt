def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def d1(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate move by best (lowest) "advantage" among visible resources
        # Lower is better for us: prefer resources we can reach sooner than opponent.
        move_best = None
        for tx, ty in res:
            self_d = d1((nx, ny), (tx, ty))
            opp_d = d1((ox, oy), (tx, ty))
            # Aggressive intercept bias: reduce score when opponent is farther.
            val = (self_d - 0.85 * opp_d, self_d, cheb((nx, ny), (tx, ty)))
            if move_best is None or val < move_best:
                move_best = val

        # Additional tie-break: prefer moves that improve current progress toward the best target
        # by minimizing distance to the single nearest resource from the new position.
        nearest_after = min(d1((nx, ny), t) for t in res)
        tie = (move_best, nearest_after, dx, dy)
        if best_val is None or tie < best_val:
            best_val = tie
            best_move = [dx, dy]

    # Fallback if all moves blocked
    if best_val is None:
        return [0, 0]
    return best_move

def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))