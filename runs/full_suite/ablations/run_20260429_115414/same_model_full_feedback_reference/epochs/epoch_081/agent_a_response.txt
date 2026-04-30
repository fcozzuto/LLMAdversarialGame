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
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target resource where we have the strongest "time advantage" over the opponent.
    best_target = resources[0]
    best_adv = -10**9
    for rx, ry in resources:
        adv = kdist(ox, oy, rx, ry) - kdist(sx, sy, rx, ry)
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    rx, ry = best_target

    # If already on target, try to block opponent by maximizing their distance from it.
    on_target = (sx == rx and sy == ry)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = kdist(nx, ny, rx, ry)
        d_opp = kdist(ox, oy, rx, ry)
        if on_target:
            # Stay on target; choose moves that increase opponent's distance from it next.
            best_opp_score = -10**18
            for odx, ody in moves:
                onx, ony = ox + odx, oy + ody
                if not valid(onx, ony):
                    continue
                best_opp_score = max(best_opp_score, kdist(onx, ony, rx, ry))
            score = 100000 - d_self + (best_opp_score)
        else:
            # Progress to target while increasing opponent separation from that same target.
            # Add a small penalty for moving away.
            score = (best_adv * 20) + (d_opp - d_self) * 10 - d_self
            # Prefer moves that also reduce opponent's "effective chasing" distance to self (intercept).
            score += max(0, kdist(ox, oy, nx, ny) - kdist(ox, oy, sx, sy))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]