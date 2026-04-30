def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # Strategic change: maximize worst-case advantage across all resources (robust contest),
    # with a small bonus for moves that keep close to *some* resource and avoid moving adjacent to opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        worst_adv = None
        best_adv = None
        near_bonus = 0
        for rx, ry in resources:
            me = cheb(nx, ny, rx, ry)
            op = cheb(ox, oy, rx, ry)
            adv = op - me  # positive => we are closer than opponent for this resource
            worst_adv = adv if worst_adv is None else (adv if adv < worst_adv else worst_adv)
            best_adv = adv if best_adv is None else (adv if adv > best_adv else best_adv)
            # bonus if this resource is within 1 move (cheb distance <=1)
            if me <= 1:
                near_bonus += 2

        opp_adj = 0
        if cheb(nx, ny, ox, oy) <= 1:
            opp_adj = -1

        # Tie-breaker: prefer moves that reduce our distance to the currently best target (largest best_adv),
        # but keep robust worst-case from being terrible.
        score = (worst_adv * 10) + (best_adv) + near_bonus + opp_adj
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break: prefer staying closer to center-ish by favoring smaller distance to board center.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            curd = abs(nx - cx) + abs(ny - cy)
            bdx, bdy = best_move
            bx, by = sx + bdx, sy + bdy
            bdist = abs(bx - cx) + abs(by - cy)
            if curd < bdist:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]