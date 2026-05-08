def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_role = (observation.get("self_role") or "").lower()
    is_pursuer = "pursuer" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if is_pursuer:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = abs(ox - nx) + abs(oy - ny)
            score = -d
            # Prefer faster capture by also moving to reduce max of axis distances
            score += -(max(abs(ox - nx), abs(oy - ny)))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Evader: look ahead a few steps, pick move maximizing best-case distance after our move.
    depth = 3
    frontier = [((sx, sy), 0)]
    seen = {(sx, sy)}
    # Evaluate each immediate move by the maximum distance reachable within remaining depth.
    move_best = {}
    for dx0, dy0 in moves:
        nx0, ny0 = sx + dx0, sy + dy0
        if not legal(nx0, ny0):
            continue
        move_best[(dx0, dy0)] = -1

    # For each candidate immediate move, BFS up to depth-1 from that neighbor.
    for (dx0, dy0) in list(move_best.keys()):
        start = (sx + dx0, sy + dy0)
        q = [(start[0], start[1], 0)]
        local_seen = {start}
        best_dist = -1
        while q:
            x, y, d = q.pop(0)
            best_dist = max(best_dist, abs(ox - x) + abs(oy - y))
            if d == depth - 1:
                continue
            nd = d + 1
            # deterministic expansion order
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in local_seen and legal(nx, ny):
                    local_seen.add((nx, ny))
                    q.append((nx, ny, nd))
        move_best[(dx0, dy0)] = best_dist

    # Tie-break: keep away even after one step (maximize current distance); then prefer cornered motion.
    def tie(dx0, dy0):
        nx, ny = sx + dx0, sy + dy0
        dist = abs(ox - nx) + abs(oy - ny)
        corner_bias = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)  # larger -> closer to center; we want smaller
        return (dist, -corner_bias)

    best_move = None
    best_val = None
    for m, v in move_best.items():
        if best_val is None or v > best_val or (v == best_val and tie(m[0], m[1]) > tie(best_move[0], best_move[1])):
            best_val = v
            best_move = m

    if best_move is None:
        # Fallback: move directly away from pursuer
        dx = 0 if sx == ox else (1 if sx > ox else -1)
        dy = 0 if sy == oy else (1 if sy > oy else -1)
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]