def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = resources[0]
        best_adv = cheb(ox, oy, best[0], best[1]) - cheb(sx, sy, best[0], best[1])
        best_ds = cheb(sx, sy, best[0], best[1])
        for rx, ry in resources[1:]:
            dS = cheb(sx, sy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            adv = dO - dS
            if adv > best_adv or (adv == best_adv and (dS < best_ds or (dS == best_ds and (rx + ry) < (best[0] + best[1])))):
                best = (rx, ry)
                best_adv = adv
                best_ds = dS
        return best

    tx, ty = best_target()

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def score_move(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        dS = cheb(nx, ny, tx, ty)
        dO = cheb(ox, oy, tx, ty)
        adv = dO - dS
        # Prefer getting closer, and also prefer moves that improve "tie-break" odds by increasing adv.
        return adv * 1000 - dS

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            sc = score_move(nx, ny)
            if sc > best_score or (sc == best_score and (dx, dy) < best_move):
                best_score = sc
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]