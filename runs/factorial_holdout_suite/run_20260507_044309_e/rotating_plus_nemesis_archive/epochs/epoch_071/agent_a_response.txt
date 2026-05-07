def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if inb(bx, by):
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd_to = None
        # Evaluate by targeting the resource that gives best (opponent advantage after we move)
        local_best = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer securing resources we can reach first; otherwise still chase if we can swing advantage.
            val = (opd - myd) * 3 - myd
            if myd < opd:
                val += 50
            elif myd == opd:
                val += 10
            # Small deterministic tie-break towards resources closer to current position
            if val > local_best:
                local_best = val
                myd_to = (myd, opd, rx, ry)
        if myd_to is None:
            continue
        if best_val is None or local_best > best_val:
            best_val = local_best
            best_move = [dx, dy]
        elif local_best == best_val:
            # deterministic tie-break: prefer smaller my cheb to the chosen resource
            cand_my = cheb(sx + dx, sy + dy, myd_to[2], myd_to[3])
            best_my = cheb(sx + best_move[0], sy + best_move[1], sy, sy)  # dummy, keep deterministic ordering
            if cand_my < best_my:
                best_move = [dx, dy]

    # If all candidate moves were invalid (shouldn't happen), stay.
    return best_move