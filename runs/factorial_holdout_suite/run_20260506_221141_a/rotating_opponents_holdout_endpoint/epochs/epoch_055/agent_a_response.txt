def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def eval_from(px, py):
        best = (-10**18, None)  # (value, target)
        for tx, ty in resources:
            sd = cheb(px, py, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # prefer nearer targets and deny those opponent can reach quickly
            value = (od - sd) * 2.0 - sd
            # slight tie-break: prefer resources closer to us
            if value > best[0] or (value == best[0] and (best[1] is None or sd < cheb(px, py, best[1][0], best[1][1]))):
                best = (value, (tx, ty))
        return best[0], best[1]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        val, _ = eval_from(nx, ny)
        # discourage aimless wandering late in game
        if observation.get("turns_remaining") is not None:
            tr = int(observation.get("turns_remaining") or 0)
            if tr < 12:
                # encourage progress to the best target
                _, tgt = eval_from(nx, ny)
                if tgt is not None:
                    val -= 0.15 * cheb(nx, ny, tgt[0], tgt[1])
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]