def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    def best_target():
        if not resources:
            return (W // 2, H // 2)
        scored = []
        for rx, ry in resources:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # Prefer resources we can beat; else prefer those that still reduce our lead deficit.
            margin = d2 - d1
            # Deterministic tie-break
            tie = (rx + ry * 7) % 997
            scored.append((margin, d1, tie, rx, ry))
        # First try to beat at least one resource; otherwise minimize our distance.
        min_margin = min(s[0] for s in scored)
        target = None
        for m, d1, tie, rx, ry in sorted(scored, key=lambda t: (-t[0], t[1], t[2])):
            if m > 0:
                target = (rx, ry)
                break
        if target is not None:
            return target
        # No winning resource: choose the one with smallest d1, tie by deterministic tie
        m, d1, tie, rx, ry = min(scored, key=lambda t: (t[1], -t[0], t[2]))
        return (rx, ry)

    tx, ty = best_target()

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ourd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # If we can reach target sooner than opponent (or tie), focus; else minimize deficit.
        # Also lightly prefer moves that keep us away from obstacles already handled by legality.
        val = (0, ourd) if ourd <= oppd else (1, ourd - oppd, ourd)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]