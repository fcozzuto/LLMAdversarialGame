def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = adj8

    # If on a resource, stay if possible; otherwise move away from immediate obstacle cluster.
    resset = {(p[0], p[1]) for p in resources}
    if (sx, sy) in resset:
        # Prefer staying if it doesn't step into danger (can't step onto obstacle anyway).
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            danger = sum(1 for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1)] if (nx+ddx, ny+ddy) in occ) + (1 if (nx, ny) in occ else 0)
            val = (2 if (nx, ny) in resset else 0) - 3 * danger - dist(nx, ny, ox, oy)
            if val > best[1]:
                best = ((dx, dy), val)
        if best[0] is None:
            return [0, 0]
        return list(best[0])

    # Pick target resource where opponent is closer; prioritize those with highest opponent advantage.
    if resources:
        best_target = None
        best_key = None
        for rx, ry in resources:
            us = dist(sx, sy, rx, ry)
            them = dist(ox, oy, rx, ry)
            # want them closer -> maximize (them - us); if equal, go nearer; if still equal, tie by coords
            key = (them - us, -us, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best_target = (rx, ry)
        tx, ty = best_target
    else:
        # No resources: move toward opponent's corner to cut off.
        tx, ty = 0, 0 if (ox, oy) != (0, 0) else (w - 1, h - 1)

    # Score candidate moves by improving our advantage toward target, collecting if possible, avoiding obstacles.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # Our advantage = (opponent distance - our distance): higher is better (we are closer / they are farther).
        cur_adv = dist(ox, oy, tx, ty) - dist(sx, sy, tx, ty)
        new_adv = dist(ox, oy, tx, ty) - dist(nx, ny, tx, ty)

        # Obstacle avoidance: penalize proximity.
        prox = 0
        for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            if (nx + ddx, ny + ddy) in occ:
                prox += 1

        # If move lands on resource, large bonus.
        gain = 1 if (nx, ny) in resset else 0

        # Small tie-break: prefer decreasing distance to target.
        dcur = dist(sx, sy, tx, ty)
        dnew = dist(nx, ny, tx, ty)
        score = (new_adv * 1000) + (gain * 500) - prox * 10 + (dcur - dnew)

        # Deterministic tie-break on move vector.
        if score > best_score or (score == best_score and (dx, dy) > best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]