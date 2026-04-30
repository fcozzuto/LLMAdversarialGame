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

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Targeting: prioritize resources we can reach first; otherwise, block by moving near contested resources.
    if resources:
        best = None
        for x, y in resources:
            dm = dist2(sx, sy, x, y)
            do = dist2(ox, oy, x, y)
            # If opponent closer, add a bigger penalty; if tie, slightly prefer nearer to opponent to contest.
            score = dm - (0.85 * do)
            if do < dm:
                score += 2.5 * (dm - do) + 120
            else:
                score -= 2.0
            # Mild preference for directionally interesting targets
            score += 0.03 * (abs(x - sx) + abs(y - sy))
            if best is None or score < best[0]:
                best = (score, x, y)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w // 2), (h // 2)

    # Choose next move by balancing: get closer to target, keep away from opponent, and avoid dead-ends.
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dtar = dist2(nx, ny, tx, ty)
        do = dist2(nx, ny, ox, oy)
        # "Cornering" avoidance: count available neighbor cells (deterministic local safe value)
        free = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay):
                free += 1
        # Stronger repulsion if close to opponent
        opp_term = 0
        if do <= 9:
            opp_term = 500
        v = dtar - 0.18 * do - 2.5 * (free == 0) + 0.01 * free + opp_term
        if bestv is None or v < bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]