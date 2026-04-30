def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Deterministic target selection: prefer resources where opponent is closer than us less.
    resources.sort(key=lambda r: (cheb(r[0], r[1], ox, oy), r[0], r[1]))
    target = None
    best = None
    for r in resources:
        d_s = cheb(r[0], r[1], sx, sy)
        d_o = cheb(r[0], r[1], ox, oy)
        # Higher means we are relatively advantaged and/or far from letting opponent grab first.
        score = (d_o - d_s) * 10 - d_s + (7 - (r[0] + r[1]) / 2.0)
        if best is None or score > best:
            best = score
            target = r

    tx, ty = target
    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_s_next = cheb(nx, ny, tx, ty)
        d_o_to_target = cheb(ox, oy, tx, ty)
        # Try to close on target while denying opponent momentum (relative advantage).
        val = (d_o_to_target - d_s_next) * 20 - d_s_next
        # Avoid walking into being immediately adjacent to opponent (deterministic mild penalty).
        if cheb(nx, ny, ox, oy) <= 1:
            val -= 8
        # Small deterministic tie-break toward decreasing distance to target, then toward corner.
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            cur_d = cheb(sx, sy, tx, ty)
            best_d = cheb(sx + best_move[0], sy + best_move[1], tx, ty)
            cand_d = d_s_next
            if cand_d < best_d or (cand_d == best_d and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]