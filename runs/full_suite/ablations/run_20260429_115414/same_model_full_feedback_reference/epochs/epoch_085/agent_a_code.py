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
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    if not resources:
        best = [0, 0]
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_target = resources[0]
    best_adv = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer than opponent
        if best_adv is None or adv > best_adv or (adv == best_adv and (sd < cheb(sx, sy, best_target[0], best_target[1]))):
            best_adv = adv
            best_target = (rx, ry)

    tx, ty = best_target

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Encourage reducing distance to target; if in a race, also keep opponent farther.
        score = -self_d + 0.15 * (opp_d - cheb(ox, oy, tx, ty))  # (second term is constant but keeps structure)
        # Directly incorporate "race swing" using our new distance vs opponent's current distance.
        score += 0.9 * (opp_d - self_d)
        # If we're currently very close, stabilize (prefer not to waste steps).
        if cheb(sx, sy, tx, ty) <= 1:
            score += 0.2 * (cheb(nx, ny, tx, ty) == 0)
        # Tie-break: move that increases our distance from opponent.
        score += 0.02 * cheb(nx, ny, ox, oy)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move