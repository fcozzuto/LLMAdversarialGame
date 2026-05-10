def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def best_for_position(nx, ny):
        if not resources:
            # Go toward far corner opposite to our start biasing toward (w-1,h-1)
            tx, ty = w - 1, h - 1
            if (ox + oy) % 2 == 0:
                tx, ty = 0, 0
            d = cheb(nx, ny, tx, ty)
            return -d - 0.001 * cheb(nx, ny, ox, oy)

        # For each resource, prefer moves where we are closer (tie favors self).
        # Weight by how strongly we beat, and encourage taking nearer targets.
        score = 0.0
        best_adv = -1e9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer
            if adv >= 0:
                # Strongly prefer winning resources; diminish when just tied.
                score += (1.0 + 0.25 * adv) / (1.0 + sd)
                if adv > best_adv:
                    best_adv = adv
            else:
                # Penalize moves that give opponent advantage; reduce penalty for far resources.
                score -= (0.35 * (-adv) + 0.1 * sd) / (1.0 + cheb(rx, ry, ox, oy))
        # Extra term: push toward any resource we can win immediately
        if best_adv < 0:
            # If we can't win any in this step, minimize distance to best target by advantage
            # (deterministic aggregate)
            mind = 10**9
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # maximize (od - sd) => minimize (sd - od)
                v = sd - od
                if v < mind:
                    mind = v
            score -= 0.3 * mind
        return score

    bestm = [0, 0]
    bestv = -1e18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = best_for_position(nx, ny)
        if v > bestv:
            bestv = v
            bestm = [dx, dy]
        elif v == bestv:
            # Deterministic tie-break: prefer not moving diagonally unless needed, then closer to opponent
            # (use a stable ordering key)
            diag = 1 if dx != 0 and dy != 0 else 0
            best_diag = 1 if bestm[0] != 0 and bestm[1] != 0 else 0
            if diag < best_diag:
                bestm = [dx, dy]
            elif diag == best_diag:
                # prefer smaller cheb to the best target (implicit), and then lexicographic
                if cheb(nx, ny, ox, oy) < cheb(sx + bestm[0], sy + bestm[1], ox, oy):
                    bestm = [dx, dy]
                elif cheb(nx, ny, ox, oy) == cheb(sx + bestm[0], sy + bestm[1], ox, oy):
                    if (dx, dy) < (bestm[0], bestm[1]):
                        bestm = [dx, dy]
    return bestm