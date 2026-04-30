def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target_score():
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer winning races and shorter distances; tie-break by coordinate.
            score = (do - ds) * 1000 - ds
            tie = -(rx + ry * 0.01)
            if best is None or (score + tie) > best[0]:
                best = (score + tie, rx, ry, ds, do)
        return best

    if resources:
        tgt = best_target_score()
        # If opponent is closer to all resources, still choose the resource that minimizes their advantage.
        if tgt is None:
            rx, ry = resources[0]
        else:
            rx, ry = int(tgt[1]), int(tgt[2])

        cur_d = cheb(sx, sy, rx, ry)
        best_move = (0, 0)
        best_val = -10**9

        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, rx, ry)
            # Boost for moving to reduce distance; small boost for staying away from opponent.
            val = (cur_d - d) * 100 - d
            val += cheb(nx, ny, ox, oy) * 0.1
            # If stepping onto a resource, strongly prefer.
            if (nx, ny) in resources:
                val += 5000
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move away from opponent (or hold if blocked).
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        val = cheb(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]