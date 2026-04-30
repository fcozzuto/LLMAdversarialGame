def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def blocked_dir(nx, ny):
        # Penalize positions that are surrounded by obstacles, to avoid dead-ends
        count = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                tx, ty = nx + dx, ny + dy
                if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
                    count += 1
        return count

    best_move = (0, 0)
    best_score = -10**9

    # Deterministic order fallback
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_to_opp = cheb(nx, ny, ox, oy)

        # Choose the best target resource for this tentative move
        # Score favors fast capture, slight preference for corner-ish resources, avoids opponent proximity.
        local_best = -10**9
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                d = 0
            else:
                d = cheb(nx, ny, rx, ry)
            # Opponent threat: if opponent is much closer to the same resource, down-weight.
            d_op = cheb(ox, oy, rx, ry)
            lead = d_op - d  # positive means we are closer
            center_bias = abs(rx - 3.5) + abs(ry - 3.5)
            val = (120 * lead) - (5 * d) - (0.8 * center_bias)
            local_best = val if val > local_best else local_best

        # Add local terrain and anti-crowding term
        terrain_pen = blocked_dir(nx, ny)
        # Prefer getting away from opponent when tie-ish (reduces contest losses)
        score = local_best - (2.0 * terrain_pen) + (0.6 * dist_to_opp)

        # Deterministic tie-break: lexicographic move preference order as listed in moves
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]