def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach no slower; otherwise pick a resource where opponent's advantage is smallest.
        claimable = 0 if ds <= do else 1
        # Tie-break: prefer closer to us and closer to center (reduces risk of getting boxed by obstacles).
        key = (claimable, ds, abs(rx - cx) + abs(ry - cy), rx, ry, do - ds)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    tx, ty = best[1], best[2]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_score = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        dself = cheb(nx, ny, tx, ty)
        dop = cheb(ox, oy, tx, ty)
        # Move that brings us closer; if equal, choose one that increases opponent's relative progress (reduce their effective reach).
        # We approximate by maximizing our post-move gap against opponent to the target.
        gap = (dop - dself)
        # Also avoid drifting away from center too much.
        center_pen = abs(nx - cx) + abs(ny - cy)
        score = (dself, -gap, center_pen, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]