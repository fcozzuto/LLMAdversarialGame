def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    # If opponent is likely stuck, greedily collect nearest; else prefer "secure first" paths.
    opp_min = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        d = dist(ox, oy, rx, ry)
        if opp_min is None or d < opp_min:
            opp_min = d
    greedy_mode = (opp_min is not None and opp_min >= 6)

    best_move = (0, 0, sx, sy)
    best_val = None

    for dx, dy, nx, ny in legal:
        if greedy_mode:
            # Prefer nearest resource; slight tie-break away from opponent.
            val = None
            nd = None
            for r in resources:
                rx, ry = int(r[0]), int(r[1])
                dself = dist(nx, ny, rx, ry)
                if nd is None or dself < nd:
                    nd = dself
                dov = dist(nx, ny, rx, ry) - dist(ox, oy, rx, ry)
                cand = (-dself, -dov)
                if val is None or cand > val:
                    val = cand
            score = val
            key = (score[0], score[1])
        else:
            # For each resource, reward being able to arrive earlier; penalize non-winning routes.
            key = None
            for r in resources:
                rx, ry = int(r[0]), int(r[1])
                dself = dist(nx, ny, rx, ry)
                dopp = dist(ox, oy, rx, ry)
                # Must be strictly earlier to "secure"; otherwise heavily penalize.
                adv = dtop = dipp = 0
                if dself < dopp:
                    adv = dopp - dself  # larger is better
                    cand = (1, adv, -dself)  # secure, bigger advantage, closer
                else:
                    # If opponent can match/beat, penalize; closer still slightly better to contest.
                    cand = (0, - (dself - dopp), -dself)
                if key is None or cand > key:
                    key = cand
            score = key

        # Deterministic final tie-break: prefer smallest resulting distance-to-opponent, then fixed move order.
        if best_val is None:
            best_val = (score, dist(nx, ny, ox, oy), dx, dy)
            best_move = (dx, dy, nx, ny)
        else:
            cur = (score, dist(nx, ny, ox, oy), dx, dy)
            if cur > best_val:
                best_val = cur
                best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]