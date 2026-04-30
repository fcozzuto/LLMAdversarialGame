def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx = ox - sx
        ty = oy - sy
        dx = 0 if tx == 0 else (1 if tx > 0 else -1)
        dy = 0 if ty == 0 else (1 if ty > 0 else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    # Pick contested resource deterministically
    best_r = None
    best_score = 10**9
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        score = md - 0.7 * od + 0.01 * (rx + 31 * ry)
        if score < best_score:
            best_score, best_r = score, (rx, ry)

    rx, ry = best_r
    md0 = cheb(sx, sy, rx, ry)

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        md = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer immediate approach; if we are behind, prioritize reducing the gap.
        val = (md0 - md) * 2.0 + (od - cheb(ox, oy, nx, ny)) * 0.05
        # Small nudge to avoid getting stuck adjacent to obstacles.
        if (nx + 1, ny) in obstacles or (nx - 1, ny) in obstacles or (nx, ny + 1) in obstacles or (nx, ny - 1) in obstacles:
            val -= 0.02
        # Deterministic tie-break: fixed move order via val compare then lexicographic
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]