def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose next position by maximizing immediate "win" margin over resources.
    best_next = (sx, sy)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # If no move changes anything, still allow.
        val = -cheb(nx, ny, ox, oy) * 0.01  # slight preference to not drift into opponent
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Positive if we are closer than opponent; stronger for being strictly closer.
            # Penalize contested/losing resources; prefer nearer wins.
            val += (do - ds) * 10.0 - ds * 0.2
        # Deterministic tie-break: prefer moves with smaller cheb to best overall resource,
        # then prefer staying still, then lexicographically.
        if val > best_val:
            best_val = val
            best_next = (nx, ny)
        elif val == best_val:
            cur_d = cheb(best_next[0], best_next[1], best_next[0], best_next[1])
            cand_d = cheb(nx, ny, nx, ny)
            if (nx, ny) == (sx, sy):
                if best_next != (sx, sy):
                    best_next = (nx, ny)
            elif best_next == (sx, sy):
                pass
            else:
                # lexicographic stable
                if (nx, ny) < best_next:
                    best_next = (nx, ny)

    return [int(best_next[0] - sx), int(best_next[1] - sy)]