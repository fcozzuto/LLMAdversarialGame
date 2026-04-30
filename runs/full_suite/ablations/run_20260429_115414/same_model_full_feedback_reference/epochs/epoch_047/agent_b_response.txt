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

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_min = min(cheb(ox, oy, rx, ry) for rx, ry in resources)

    best = None
    best_adv = None
    best_tiebreak = None

    # Evaluate moves by advantage in reaching the closest remaining resource.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if any(nx == rx and ny == ry for rx, ry in resources):
            return [dx, dy]

        my_min = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        # Advantage: how much closer we are than opponent's best-to-resource.
        adv = (opp_min - my_min)

        # Tie-break deterministically: prefer smaller my_min, then prefer staying on diagonals less (more direct).
        tiebreak = (my_min, abs(dx) + abs(dy), dx, dy)
        if best_adv is None or adv > best_adv or (adv == best_adv and tiebreak < best_tiebreak):
            best_adv = adv
            best_tiebreak = tiebreak
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]