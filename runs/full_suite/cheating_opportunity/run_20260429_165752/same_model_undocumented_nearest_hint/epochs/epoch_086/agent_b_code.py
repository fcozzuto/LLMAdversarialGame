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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_choice = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
                continue
            best_for_this_move = None
            # Choose the resource where (opponent distance - self distance) is maximized after this move.
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                adv = d_opp - d_self
                cand = (adv, -d_self, rx, ry)  # tie-break: prefer smaller self distance, then lexicographic resource
                if best_for_this_move is None or cand > best_for_this_move:
                    best_for_this_move = cand
            # Additional preference: if we are close to any resource, prioritize.
            # Penalize moves that worsen minimum distance to resources.
            min_d_after = 10**9
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                if d_self < min_d_after:
                    min_d_after = d_self
            overall = (best_for_this_move[0], best_for_this_move[1], -min_d_after, -abs((nx - (W//2))) - abs((ny - (H//2))), nx, ny)
            if best_choice is None or overall > best_choice:
                best_choice = overall
        if best_choice is not None:
            _, _, _, _, tx, ty = best_choice
            return [tx - sx, ty - sy]

    # Fallback: move deterministically toward center while avoiding obstacles.
    cx, cy = W // 2, H // 2
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue
        score = (-cheb(nx, ny, cx, cy), nx, ny)
        if best is None or score > best:
            best = score
            bx, by = nx, ny
    return [bx - sx, by - sy] if best is not None else [0, 0]