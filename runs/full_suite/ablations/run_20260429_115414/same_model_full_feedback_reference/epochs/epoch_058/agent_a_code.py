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
    if not resources:
        return [0, 0]

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
    best_adv = -10**9
    best_dist = 10**9
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # prefer where opponent is further than us
        key = (rx * 100 + ry)  # deterministic tie-breaker
        if adv > best_adv or (adv == best_adv and (myd < best_dist or (myd == best_dist and key < best_key))):
            best_adv = adv
            best_dist = myd
            best_r = (rx, ry)
            best_key = key

    rx, ry = best_r
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue

        myd2 = cheb(nx, ny, rx, ry)
        # estimate how our move affects opponent contest on same target
        opd = cheb(ox, oy, rx, ry)
        opp_next_threat = 0
        # If we're at/near target or can block adjacency, prefer staying/advancing.
        if max(abs(nx - rx), abs(ny - ry)) <= 1:
            opp_next_threat += 3
        if myd2 < best_dist:
            opp_next_threat += 1

        # Main objective: minimize our distance, while maximizing advantage vs opponent
        val = 100 * (best_adv - (opd - myd2))  # increase when (opd - myd2) is larger
        val += -10 * myd2
        val += opp_next_threat

        # Small preference for moving generally toward the target to prevent oscillation
        val += -1 * cheb(nx, ny, rx, ry)

        # Deterministic tie-break
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]