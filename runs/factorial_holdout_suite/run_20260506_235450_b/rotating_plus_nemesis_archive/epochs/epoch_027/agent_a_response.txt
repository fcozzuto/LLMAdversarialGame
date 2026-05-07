def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    raw_obs = observation.get("obstacles") or []
    obstacles = set()
    for p in raw_obs:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonals)

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = r[0], r[1]
            if (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # pick a target once per turn: prefer resources we can arrive earlier than opponent;
    # if none, pick the one that least favors them (smallest opp - self).
    self_dists = [(dist((sx, sy), t), dist((ox, oy), t), t) for t in res]
    candidates = [it for it in self_dists if it[0] < it[1]]
    if candidates:
        # among winning targets, choose smallest (self_dist) then largest slack
        candidates.sort(key=lambda z: (z[0], -((z[1] - z[0]))))
    else:
        # otherwise, choose target that minimizes advantage to opponent
        candidates.sort(key=lambda z: (z[1] - z[0], z[1]))
    target = candidates[0][2]

    tx, ty = target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # If we can grab immediately, do it.
        pickup = 1 if (nx, ny) in set(res) else 0

        # Advantage score if pursuing chosen target.
        d_self = dist((nx, ny), target)
        d_opp = dist((ox, oy), target)

        # Discourage moving into opponent-adjacent squares when not picking up.
        opp_adj = max(abs(nx - ox), abs(ny - oy))
        danger = 2 if opp_adj <= 1 else 0

        # Small bias to stay aligned with sweep pressure: reduce row difference (sweep rows archetype).
        row_bias = -abs(ny - oy) * 0.05

        score = 1000 * pickup + (d_opp - d_self) * 10 + row_bias - danger * 25

        # Deterministic tie-breaker: prefer smaller movement, then lexicographically.
        move_mag = abs(dx) + abs(dy)
        if pickup == 0:
            score -= move_mag * 0.01

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]