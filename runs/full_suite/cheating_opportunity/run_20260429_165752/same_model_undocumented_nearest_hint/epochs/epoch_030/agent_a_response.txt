def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_res = None
        best_score = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            tie_break = (rx + 3 * ry) % 7
            # Prefer resources where we are closer by margin; if losing, still pick nearest that limits deficit.
            score = (do - ds, -ds, tie_break)
            if best_score is None or score > best_score:
                best_score = score
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        # No resources: drift to center while slightly biasing away from opponent.
        tx, ty = (W - 1) // 2, (H - 1) // 2

    # Greedy one-step toward target, but avoid making it easier for opponent by preferring moves that keep/extend margin.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        cur_ds = cheb(sx, sy, tx, ty)
        nxt_ds = cheb(nx, ny, tx, ty)
        cur_margin = cheb(ox, oy, tx, ty) - cur_ds
        nxt_margin = cheb(ox, oy, tx, ty) - nxt_ds
        # Primary: increase margin; Secondary: reduce distance; Tertiary: keep deterministic tie-break by coords.
        val = (nxt_margin, -nxt_ds, (nx + 5 * ny) % 11, -(abs(dx) + abs(dy)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]