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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_obstacle_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Advantage against opponent for the best reachable resource from this move.
        # Score = max over resources of (opp_dist - self_dist), with small tie-breakers.
        best_adv = None
        best_tieb = None
        for tx, ty in resources:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = od - sd
            tieb = (sd, tx, ty)
            if best_adv is None or adv > best_adv or (adv == best_adv and tieb < best_tieb):
                best_adv = adv
                best_tieb = tieb

        # Strategically: move to improve advantage; if no advantage, still reduce self distance.
        self_dist_to_best = best_tieb[0]
        block_pen = adj_obstacle_count(nx, ny)  # prefer less clutter near obstacles
        # Mildly avoid getting too close to opponent unless it helps advantage.
        opp_dist = cheb(nx, ny, ox, oy)
        # Total score (higher is better). Deterministic and bounded.
        score = (best_adv * 1000) + (-self_dist_to_best * 10) + (opp_dist) - (block_pen * 2)

        if best_score is None or score > best_score or (score == best_score and (nx, ny) < (best_move[0] + sx, best_move[1] + sy)):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]