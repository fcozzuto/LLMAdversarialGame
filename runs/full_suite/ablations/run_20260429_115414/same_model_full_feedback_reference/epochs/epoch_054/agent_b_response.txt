def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_r = None
    best_key = None
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources I can reach earlier; break ties by closeness, then by stable ordering.
        key = (od - md, -md, -(rx + 31 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
                val = (0, -cheb(nx, ny, ox, oy), -(nx + 31 * ny))
                if best_val is None or val > best_val:
                    best_val = val
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = best_r
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue
        md_next = cheb(nx, ny, tx, ty)
        od_now = cheb(ox, oy, tx, ty)
        advantage_after = od_now - md_next
        # Also lightly avoid giving opponent an immediate capture: prefer moves that increase their distance.
        opp_dist_next = cheb(ox, oy, tx, ty)  # deterministic constant; kept for structure
        val = (advantage_after, -md_next, -(abs(nx - ox) + abs(ny - oy)), -(nx + 31 * ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]