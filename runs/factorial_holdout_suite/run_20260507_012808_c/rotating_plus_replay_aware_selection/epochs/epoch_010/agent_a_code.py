def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    adj_obs = set()
    for x, y in obstacles:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    adj_obs.add((nx, ny))

    # Select a target resource: prefer ones we can arrive no later than opponent.
    if resources:
        best = None
        for rx, ry in resources:
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # If contested, strongly prefer being closer/equal; otherwise prefer the closest available.
            if sd <= od:
                score = 1000 * (od - sd + 1) - 10 * sd
            else:
                score = - (sd + 2 * (sd - od))  # smaller is better; make worse if much farther than opponent
            # Small bias away from edges if tied to reduce getting stuck near corners/obstacles.
            edge_bias = 0
            if rx == 0 or rx == w - 1:
                edge_bias += 1
            if ry == 0 or ry == h - 1:
                edge_bias += 1
            score -= edge_bias
            if best is None or score > best[0]:
                best = (score, rx, ry)
        _, tx, ty = best
    else:
        # No visible resources: head to the farthest corner from opponent (acts like opportunistic interception).
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: dist(c, (ox, oy)))

    # Evaluate immediate moves: go toward target, avoid obstacle adjacency, and slightly deny opponent by moving closer to our own target.
    def step_penalty(nx, ny):
        p = 0
        if (nx, ny) in adj_obs:
            p += 8
        # discourage moving into cells closer to opponent than we are, to reduce being "shadowed"
        if dist((nx, ny), (ox, oy)) < dist((sx, sy), (ox, oy)):
            p += 2
        return p

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_to_t = dist((nx, ny), (tx, ty))
        d_to_t_now = dist((sx, sy), (tx, ty))
        # Prefer reductions; otherwise keep shortest.
        toward = d_to_t_now - d_to_t
        key = (-(toward), d_to_t, step_penalty(nx, ny), abs(nx - tx) + abs(ny - ty))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]