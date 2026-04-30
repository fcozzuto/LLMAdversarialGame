def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    cx, cy = W // 2, H // 2
    best_move = (0, 0)
    best_val = -10**18

    # Target selection: prefer resources where we are not worse, especially near.
    targets = resources[:]
    if targets:
        # Deterministic ordering for tie-breaking
        targets.sort(key=lambda r: (-(cheb(sx, sy, r[0], r[1]) - cheb(ox, oy, r[0], r[1])), r[0], r[1]))
        targets = targets[:6]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Base: move towards center slightly to avoid dead ends
        val = -0.12 * cheb(nx, ny, cx, cy)
        # Evaluate move by best resource outcome after stepping
        if targets:
            local = -10**18
            for rx, ry in targets:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # If we can arrive earlier or tie, heavily rewarded; otherwise penalized.
                adv = od - sd
                # Encourage shorter paths and avoid over-committing when far behind
                score = (adv * 3.0) - (sd * 0.6) - (0.15 if (rx == nx and ry == ny) else 0.0)
                if score > local:
                    local = score
            # Small preference for moves that keep our advantage improving over staying
            stay_sd = cheb(sx, sy, targets[0][0], targets[0][1]) if targets else 0
            val += local
        else:
            val += -cheb(nx, ny, cx, cy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]