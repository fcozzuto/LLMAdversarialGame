def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = [(p[0], p[1]) for p in observation["resources"]]
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = -cheb(nx, ny, ox, oy)  # drift away
            if score > best[2]:
                best = (dx, dy, score)
        return [best[0], best[1]]

    # Pick a target resource where we are relatively closer than the opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds - do, ds)  # prioritize being closer than opponent
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    tx, ty = best_res

    # Choose move maximizing progress to target while avoiding opponent proximity.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_after = cheb(nx, ny, tx, ty)
        d_self = cheb(sx, sy, tx, ty)
        progress = d_self - d_after  # positive is good
        d_opp = cheb(nx, ny, ox, oy)
        # Encourage blocking less (stay a bit away), but allow being close if it yields progress.
        score = progress * 10.0 + d_opp * 0.15 - d_after * 1.0
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]